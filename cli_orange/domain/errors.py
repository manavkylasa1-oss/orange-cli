class DomainError(Exception):
    pass

class AuthError(DomainError):
    pass

class NotFound(DomainError):
    pass