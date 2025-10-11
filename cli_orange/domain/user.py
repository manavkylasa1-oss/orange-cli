from dataclasses import dataclass

@dataclass
class User:
    username: str
    password_hash: str
    first_name: str
    last_name: str
    balance: float = 0.0
    is_admin: bool = False
