# cli_orange/orange_db/db.py
from __future__ import annotations

import pickle
from pathlib import Path
from typing import Dict

from cli_orange.domain.user import User
from cli_orange.domain.portfolio import Portfolio
from cli_orange.domain.security import Security

USERS: Dict[str, User] = {}
PORTFOLIOS: Dict[str, Portfolio] = {}

SECURITIES = {
    "AAPL": Security("AAPL", "Apple", 100.00),
    "MSFT": Security("MSFT", "Microsoft", 120.00),
    "GOOG": Security("GOOG", "Alphabet", 150.00),
    "TSLA": Security("TSLA", "Tesla", 90.00),
    "NVDA": Security("NVDA", "Nvidia", 200.00),
}

_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_STATE_FILE = _DATA_DIR / "state.pkl"

def load_state() -> None:
    if not _STATE_FILE.exists():
        return
    try:
        with _STATE_FILE.open("rb") as f:
            state = pickle.load(f)
        USERS.clear(); USERS.update(state.get("USERS", {}))
        PORTFOLIOS.clear(); PORTFOLIOS.update(state.get("PORTFOLIOS", {}))
    except Exception:
        pass

def save_state() -> None:
    try:
        with _STATE_FILE.open("wb") as f:
            pickle.dump({"USERS": USERS, "PORTFOLIOS": PORTFOLIOS}, f)
    except Exception:
        pass
