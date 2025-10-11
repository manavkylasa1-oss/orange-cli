# cli_orange/cli/menu_printer.py
from typing import Dict, Iterable, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

class MenuPrinter:
    def __init__(self, menus: Dict[int, str], console: Optional[Console] = None):
        self.console = console or Console()
        self.menus = menus

    def clear(self):
        self.console.clear()

    def header(self, title: str):
        self.console.rule(f"[bold]{title}[/bold]")

    def info(self, msg: str):
        self.console.print(f"[cyan]ℹ {msg}[/cyan]")

    def success(self, msg: str):
        self.console.print(f"[green]✓ {msg}[/green]")

    def warn(self, msg: str):
        self.console.print(f"[yellow]⚠ {msg}[/yellow]")

    def error(self, msg: str):
        self.console.print(f"[red]✖ {msg}[/red]")

    def print_menu(self, menu_id: int):
        self.console.print(Panel.fit(self.menus[menu_id], border_style="cyan"))

    def print_table(self, title: str, columns: Iterable[str], rows: Iterable[Iterable[object]]):
        t = Table(title=title)
        numeric_cols = {"qty", "quantity", "price", "cost", "balance", "amount", "total"}
        for c in columns:
            justify = "right" if c.lower() in numeric_cols else "left"
            t.add_column(c, justify=justify)
        for r in rows:
            t.add_row(*[str(x) for x in r])
        self.console.print(t)

    def pause(self):
        Prompt.ask("Press [Enter] to continue", default="")

    def ask_text(self, prompt: str) -> str:
        return Prompt.ask(prompt).strip()

    def ask_password(self, prompt: str) -> str:
        return Prompt.ask(prompt, password=True)

    def ask_float(self, prompt: str, minimum: float = float("-inf")) -> float:
        """Ask for a float and enforce a minimum (default: no lower bound)."""
        while True:
            value = Prompt.ask(prompt).strip()
            try:
                num = float(value)
                if num < minimum:
                    self.warn(f"Enter a value ≥ {minimum}.")
                    continue
                return num
            except ValueError:
                self.warn("Enter a numeric value.")
