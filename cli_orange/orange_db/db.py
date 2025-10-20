# cli_orange/orange_db/db.py
from __future__ import annotations

import os
import pickle
from pathlib import Path
from typing import Dict

# Domain objects are already used across the app; persisting them directly is the
# simplest way to keep compatibility with your existing services.
# (For a real app, you'd do JSON + explicit (de)serialization.)
from cli_orange.domain.user import User        # adjust the import path if your file is named differently
from cli_orange.domain.portfolio import Portfolio

# -------------------------
# In-memory data structures
# -------------------------
USERS: Dict[str, User] = {}
PORTFOLIOS: Dict[str, Portfolio] = {}

# Marketplace catalog (static; not persisted)
SECURITIES: Dict[str, str] = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOG": "Alphabet",
    "TSLA": "Tesla",
    "NVDA": "Nvidia",
}

# -------------------------
# Persistence configuration
# -------------------------
_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_STATE_FILE = _DATA_DIR / "state.pkl"


def load_state() -> None:
    """Load USERS and PORTFOLIOS from disk if present."""
    if not _STATE_FILE.exists():
        return
    try:
        with _STATE_FILE.open("rb") as f:
            state = pickle.load(f)
        USERS.clear()
        USERS.update(state.get("USERS", {}))
        PORTFOLIOS.clear()
        PORTFOLIOS.update(state.get("PORTFOLIOS", {}))
    except Exception:
        # Corrupt/old file? ignore so the app can still boot.
        pass


def save_state() -> None:
    """Persist USERS and PORTFOLIOS to disk."""
    try:
        with _STATE_FILE.open("wb") as f:
            pickle.dump({"USERS": USERS, "PORTFOLIOS": PORTFOLIOS}, f)
    except Exception:
        # For this CLI, fail silently; in a real app, log this.
        pass
