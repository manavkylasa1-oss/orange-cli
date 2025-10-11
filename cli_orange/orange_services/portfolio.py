import uuid
from typing import Iterable
from cli_orange.domain.errors import DomainError
from cli_orange.domain.portfolio import Portfolio
from cli_orange.orange_db.db import USERS, PORTFOLIOS

class PortfolioService:
    def list_by_owner(self, owner_username: str) -> Iterable[Portfolio]:
        return [p for p in PORTFOLIOS.values() if p.owner == owner_username]

    def create(self, owner_username: str, name: str, strategy: str) -> Portfolio:
        if owner_username not in USERS:
            raise DomainError("Owner not found.")
        pid = str(uuid.uuid4())[:8]
        p = Portfolio(id=pid, owner=owner_username, name=name, strategy=strategy)
        PORTFOLIOS[pid] = p
        return p

    def delete(self, owner_username: str, portfolio_id: str) -> None:
        p = PORTFOLIOS.get(portfolio_id)
        if not p or p.owner != owner_username:
            raise DomainError("Portfolio not found.")
        PORTFOLIOS.pop(portfolio_id)

    def buy(self, owner_username: str, portfolio_id: str, ticker: str, quantity: float, price: float):
        if quantity <= 0:
            raise DomainError("Quantity must be > 0.")
        if price < 0:
            raise DomainError("Price must be >= 0.")
        user = USERS.get(owner_username)
        p = PORTFOLIOS.get(portfolio_id)
        if not user or not p or p.owner != owner_username:
            raise DomainError("User/Portfolio not found.")
        required = quantity * price
        if user.balance < required:
            raise DomainError("Insufficient balance.")
        user.balance -= required
        p.add(ticker.upper(), quantity)

    def sell(self, owner_username: str, portfolio_id: str, ticker: str, quantity: float, price: float):
        if quantity <= 0:
            raise DomainError("Quantity must be > 0.")
        if price < 0:
            raise DomainError("Price must be >= 0.")
        user = USERS.get(owner_username)
        p = PORTFOLIOS.get(portfolio_id)
        if not user or not p or p.owner != owner_username:
            raise DomainError("User/Portfolio not found.")
        t = ticker.upper()
        if not p.has(t, quantity):
            raise DomainError("Not enough quantity to sell.")
        proceeds = quantity * price
        p.add(t, -quantity)
        user.balance += proceeds
