# cli_orange/domain/portfolio.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple

# Domain model ---------------------------------------------------------------

@dataclass
class Portfolio:
    id: str
    owner: str           # username (was 'user' in your service code)
    name: str
    strategy: str
    holdings: Dict[str, float] = field(default_factory=dict)

    def add(self, ticker: str, qty: float):
        self.holdings[ticker] = self.holdings.get(ticker, 0.0) + qty
        if self.holdings[ticker] <= 0:
            self.holdings.pop(ticker, None)

    def has(self, ticker: str, qty: float) -> bool:
        return self.holdings.get(ticker, 0.0) >= qty


