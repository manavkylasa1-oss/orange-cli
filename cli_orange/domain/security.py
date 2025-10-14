# cli_orange/domain/security.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Security:
    ticker: str
    issuer: str
    price: float
