
from typing import Iterable
from cli_orange.domain.user import User
from cli_orange.domain.errors import DomainError
from cli_orange.orange_db.db import USERS
from .auth import AuthService

class UsersService:
    def __init__(self, auth: AuthService):
        self.auth = auth

    def list_all(self) -> Iterable[User]:
        return list(USERS.values())

    def create(self, username: str, password: str, first_name: str, last_name: str,
               balance: float = 0.0, is_admin: bool = False) -> User:
        if username in USERS:
            raise DomainError("Username already exists.")
        if balance < 0:
            raise DomainError("Balance must be >= 0.")
        user = User(
            username=username,
            password_hash=self.auth.hash_password(password),
            first_name=first_name,
            last_name=last_name,
            balance=balance,
            is_admin=is_admin,
        )
        USERS[username] = user
        return user

    def delete(self, username: str) -> None:
        if username == "admin":
            raise DomainError("Admin user cannot be deleted.")
        if username not in USERS:
            raise DomainError("User not found.")
        USERS.pop(username)
