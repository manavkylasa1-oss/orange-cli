# cli_orange/main.py
from __future__ import annotations

import re
from rich.console import Console

from cli_orange.cli.menu_printer import MenuPrinter
from cli_orange.cli.constants import (
    MENUS, LOGIN_MENU, MAIN_MENU, MANAGE_USERS, MANAGE_PORTFOLIOS, MARKETPLACE
)
from cli_orange.domain.errors import DomainError, AuthError

from cli_orange.orange_services.auth import AuthService
from cli_orange.orange_services.users_services import UsersService
from cli_orange.orange_services.portfolio import PortfolioService
from cli_orange.orange_db.db import USERS, SECURITIES, load_state, save_state

console = Console()


# ---------- helpers ----------
def _parse_tickers(line: str) -> list[str]:
    """Split 'AAPL, msft tsla' into ['AAPL','MSFT','TSLA']."""
    return [tok.upper() for tok in re.split(r"[,\s]+", line.strip()) if tok]


def _resolve_portfolio_id(portfolios_service: PortfolioService, owner_username: str, pid_or_name: str) -> str:
    """Accept either a portfolio ID or an exact portfolio Name; return the ID."""
    for p in portfolios_service.list_by_owner(owner_username):
        if p.id == pid_or_name or p.name == pid_or_name:
            return p.id
    raise DomainError("Portfolio not found.")


# ---------- app ----------
def run():
    # load persisted users/portfolios
    load_state()

    ui = MenuPrinter(MENUS, console)
    auth = AuthService()
    users = UsersService(auth)
    portfolios = PortfolioService()

    # seed admin if missing
    if "admin" not in USERS:
        users.create("admin", "adminpass", "Admin", "User", balance=1000.0, is_admin=True)
        save_state()

    logged_in = None
    current = LOGIN_MENU

    while True:
        try:
            # ---------------- LOGIN / SIGN-UP ----------------
            if current == LOGIN_MENU:
                ui.clear(); ui.header("Portfolio CLI"); ui.print_menu(LOGIN_MENU)
                c = ui.ask_text("> ")

                if c == "0":
                    ui.info("Bye!")
                    save_state()
                    break

                elif c == "1":  # admin login
                    username = ui.ask_text("Username")
                    password = ui.ask_password("Password")
                    try:
                        user = auth.login(username, password)
                        if not user.is_admin:
                            ui.error("This account is not an admin. Use 'User login'."); ui.pause(); continue
                        logged_in = user
                        ui.success(f"Welcome, {user.first_name}!")
                        current = MAIN_MENU
                    except AuthError as e:
                        ui.error(str(e)); ui.pause()
                    continue

                elif c == "2":  # user login
                    username = ui.ask_text("Username")
                    password = ui.ask_password("Password")
                    try:
                        user = auth.login(username, password)
                        logged_in = user
                        ui.success(f"Welcome, {user.first_name}!")
                        current = MAIN_MENU
                    except AuthError as e:
                        ui.error(str(e)); ui.pause()
                    continue

                elif c == "3":  # sign-up
                    ui.header("Create your account")
                    uname = ui.ask_text("Choose a username")
                    if uname == "admin":
                        ui.error("Username 'admin' is reserved."); ui.pause(); continue
                    pwd = ui.ask_password("Choose a password")
                    fn = ui.ask_text("First name")
                    ln = ui.ask_text("Last name")
                    bal = ui.ask_float("Initial cash balance", minimum=0.0)

                    try:
                        new_user = users.create(uname, pwd, fn, ln, bal, is_admin=False)
                        save_state()
                        ui.success("Account created.")

                        # create first portfolio?
                        if ui.ask_text("Create your first portfolio now? (y/n)").lower().startswith("y"):
                            name = ui.ask_text("Portfolio name")
                            strat = ui.ask_text("Strategy (free text)")
                            created_portfolio = portfolios.create(new_user.username, name=name, strategy=strat)
                            save_state()
                            ui.success(f"Created portfolio {created_portfolio.id}.")

                            # add securities right away?
                            batch: list[tuple[str, float, float, float]] = []
                            if ui.ask_text("Add securities now? (y/n)").lower().startswith("y"):
                                while True:
                                    ui.print_table("Marketplace", ["Ticker", "Name"], list(SECURITIES.items()))
                                    tickers_line = ui.ask_text("Ticker(s) (space/comma separated)")
                                    tickers = _parse_tickers(tickers_line)
                                    qty = ui.ask_float("Quantity (applied to each)", minimum=0.0001)
                                    price = ui.ask_float("Purchase price (applied to each)", minimum=0.0)
                                    for t in tickers:
                                        try:
                                            portfolios.buy(new_user.username, created_portfolio.id, t, qty, price)
                                            save_state()
                                            ui.success(f"Purchase completed: {t} x {qty} @ {price}")
                                            batch.append((t, qty, price, qty * price))
                                        except DomainError as e:
                                            ui.error(f"{t}: {e}")
                                    if not ui.ask_text("Add another security? (y/n)").lower().startswith("y"):
                                        break

                            if batch:
                                total = sum(c for *_, c in batch)
                                ui.print_table(
                                    "Initial Purchase Allocation",
                                    ["Ticker", "Qty", "Price", "Cost"],
                                    [(t, q, f"{p:.2f}", f"{c:.2f}") for (t, q, p, c) in batch]
                                )
                                ui.info(f"Total spent: {total:.2f}")
                                ui.info(f"Cash balance: {new_user.balance:.2f}")
                                ui.pause()

                        # auto-login
                        logged_in = new_user
                        ui.success(f"Welcome, {new_user.first_name}!")
                        current = MAIN_MENU

                    except DomainError as e:
                        ui.error(str(e)); ui.pause()
                    continue

                else:
                    ui.warn("Invalid option."); ui.pause(); continue

            # ---------------- MAIN MENU ----------------
            ui.clear(); ui.header("Portfolio CLI"); ui.print_menu(MAIN_MENU)
            c = ui.ask_text("> ")

            if c == "0":
                ui.info("Goodbye!")
                save_state()
                break

            # Manage Users (ADMIN ONLY)
            elif c == "1":
                if not logged_in.is_admin:
                    ui.error("Admins only.")
                    if ui.ask_text("Switch to Admin login now? (y/n)").lower().startswith("y"):
                        logged_in = None
                        current = LOGIN_MENU
                    else:
                        ui.pause()
                    continue

                while True:
                    ui.clear(); ui.header("Manage Users"); ui.print_menu(MANAGE_USERS)
                    sub = ui.ask_text("> ")
                    if sub == "9": break

                    elif sub == "1":  # view users
                        rows = [
                            (u.username, u.first_name, u.last_name, f"{u.balance:.2f}", "Y" if u.is_admin else "N")
                            for u in users.list_all()
                        ]
                        ui.print_table("Users", ["Username", "First", "Last", "Balance", "Admin"], rows)
                        ui.pause()

                    elif sub == "2":  # create user
                        uname = ui.ask_text("New username")
                        if uname == "admin": ui.error("Use a different username."); ui.pause(); continue
                        pwd = ui.ask_password("New password")
                        fn = ui.ask_text("First name"); ln = ui.ask_text("Last name")
                        bal = ui.ask_float("Starting balance", minimum=0.0)
                        try:
                            users.create(uname, pwd, fn, ln, bal, is_admin=False)
                            save_state()
                            ui.success("User created.")
                        except DomainError as e:
                            ui.error(str(e))
                        ui.pause()

                    elif sub == "3":  # delete user
                        uname = ui.ask_text("Username to delete")
                        try:
                            users.delete(uname)
                            save_state()
                            ui.success("User deleted.")
                        except DomainError as e:
                            ui.error(str(e))
                        ui.pause()

                    else:
                        ui.warn("Invalid option."); ui.pause()

            # Manage Portfolios
            elif c == "2":
                while True:
                    ui.clear(); ui.header("Manage Portfolios"); ui.print_menu(MANAGE_PORTFOLIOS)
                    sub = ui.ask_text("> ")
                    if sub == "9": break

                    elif sub == "1":  # view my portfolios
                        rows = []
                        for p in portfolios.list_by_owner(logged_in.username):
                            holdings = "\n".join(f"{t}: {q}" for t, q in p.holdings.items()) or "-"
                            rows.append((p.name, p.strategy, holdings, p.id))
                        ui.print_table("Your Portfolios", ["Name", "Strategy", "Holdings", "ID"], rows)
                        ui.pause()

                    elif sub == "2":  # create new portfolio
                        name = ui.ask_text("Portfolio name")
                        strat = ui.ask_text("Strategy")
                        p = portfolios.create(owner_username=logged_in.username, name=name, strategy=strat)
                        save_state()
                        ui.success(f"Created portfolio {p.id}.")

                        # offer to add securities now (multi-ticker)
                        if ui.ask_text("Add securities now? (y/n)").lower().startswith("y"):
                            add_batch: list[tuple[str, float, float, float]] = []
                            while True:
                                ui.print_table("Marketplace", ["Ticker", "Name"], list(SECURITIES.items()))
                                tickers_line = ui.ask_text("Ticker(s) (space/comma separated)")
                                tickers = _parse_tickers(tickers_line)
                                qty = ui.ask_float("Quantity (applied to each)", minimum=0.0001)
                                price = ui.ask_float("Purchase price (applied to each)", minimum=0.0)
                                for t in tickers:
                                    try:
                                        portfolios.buy(logged_in.username, p.id, t, qty, price)
                                        save_state()
                                        ui.success(f"Purchase completed: {t} x {qty} @ {price}")
                                        add_batch.append((t, qty, price, qty * price))
                                    except DomainError as e:
                                        ui.error(f"{t}: {e}")
                                if not ui.ask_text("Add another? (y/n)").lower().startswith("y"):
                                    break

                            if add_batch:
                                total = sum(c for *_, c in add_batch)
                                ui.print_table(
                                    f"Purchases for {p.name}",
                                    ["Ticker", "Qty", "Price", "Cost"],
                                    [(t, q, f"{pr:.2f}", f"{c:.2f}") for (t, q, pr, c) in add_batch]
                                )
                                ui.info(f"Total spent: {total:.2f}")
                                ui.info(f"Cash balance: {logged_in.balance:.2f}")

                        ui.pause()

                    elif sub == "3":  # delete portfolio
                        pid_or_name = ui.ask_text("Portfolio name or ID")
                        try:
                            pid = _resolve_portfolio_id(portfolios, logged_in.username, pid_or_name)
                            portfolios.delete(owner_username=logged_in.username, portfolio_id=pid)
                            save_state()
                            ui.success("Portfolio deleted.")
                        except DomainError as e:
                            ui.error(str(e))
                        ui.pause()

                    elif sub == "4":  # sell / liquidate
                        pid_or_name = ui.ask_text("Portfolio name or ID")
                        try:
                            pid = _resolve_portfolio_id(portfolios, logged_in.username, pid_or_name)
                        except DomainError as e:
                            ui.error(str(e)); ui.pause(); continue
                        ticker = ui.ask_text("Ticker").upper()
                        qty = ui.ask_float("Quantity to sell", minimum=0.0001)
                        price = ui.ask_float("Sale price", minimum=0.0)
                        try:
                            portfolios.sell(logged_in.username, pid, ticker, qty, price)
                            save_state()
                            ui.success("Sale completed.")
                            ui.info(f"Cash balance: {logged_in.balance:.2f}")
                        except DomainError as e:
                            ui.error(str(e))
                        ui.pause()

                    else:
                        ui.warn("Invalid option."); ui.pause()

            # Marketplace
            elif c == "3":
                while True:
                    ui.clear(); ui.header("Marketplace"); ui.print_menu(MARKETPLACE)
                    sub = ui.ask_text("> ")
                    if sub == "9": break

                    elif sub == "1":  # view catalog
                        ui.print_table("Marketplace", ["Ticker", "Name"], list(SECURITIES.items()))
                        ui.pause()

                    elif sub == "2":  # place purchase order (multi-ticker)
                        pid_or_name = ui.ask_text("Portfolio name or ID")
                        try:
                            pid = _resolve_portfolio_id(portfolios, logged_in.username, pid_or_name)
                        except DomainError as e:
                            ui.error(str(e)); ui.pause(); continue

                        session_batch: list[tuple[str, float, float, float]] = []
                        while True:
                            ui.print_table("Marketplace", ["Ticker", "Name"], list(SECURITIES.items()))
                            tickers_line = ui.ask_text("Ticker(s) (space/comma separated)")
                            tickers = _parse_tickers(tickers_line)
                            qty = ui.ask_float("Quantity (applied to each)", minimum=0.0001)
                            price = ui.ask_float("Purchase price (applied to each)", minimum=0.0)
                            for t in tickers:
                                try:
                                    portfolios.buy(logged_in.username, pid, t, qty, price)
                                    save_state()
                                    ui.success(f"Purchase completed: {t} x {qty} @ {price}")
                                    session_batch.append((t, qty, price, qty * price))
                                except DomainError as e:
                                    ui.error(f"{t}: {e}")
                            if not ui.ask_text("Add another security? (y/n)").lower().startswith("y"):
                                break

                        if session_batch:
                            total = sum(c for *_, c in session_batch)
                            ui.print_table(
                                "Purchase Allocation",
                                ["Ticker", "Qty", "Price", "Cost"],
                                [(t, q, f"{p:.2f}", f"{c:.2f}") for (t, q, p, c) in session_batch]
                            )
                            ui.info(f"Total spent: {total:.2f}")
                            ui.info(f"Cash balance: {logged_in.balance:.2f}")
                            ui.pause()

                    else:
                        ui.warn("Invalid option."); ui.pause()

            else:
                ui.warn("Invalid option."); ui.pause()

        except (DomainError, AuthError) as e:
            console.print(f"[red]Error:[/red] {e}"); ui.pause()
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Bye![/yellow]")
            save_state()
            break
        except Exception as e:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}"); ui.pause()
