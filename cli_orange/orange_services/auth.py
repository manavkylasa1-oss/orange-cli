import hashlib
from cli_orange.domain.errors import AuthError
from cli_orange.orange_db.db import USERS


def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

class AuthService:
    def login(self, username: str, password: str):
        user = USERS.get(username)
        if not user:
            raise AuthError("Unknown user.")
        if user.password_hash != _hash(password):
            raise AuthError("Invalid credentials.")
        return user

    def hash_password(self, plain: str) -> str:
        return _hash(plain)
