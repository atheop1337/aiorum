from functools import lru_cache

class TokenValidationError(Exception):
    pass

@lru_cache()
def validate_token(token: str) -> bool:
    if not isinstance(token, str):
        raise TokenValidationError(
            f"Token type {type(token)} not supported, must be str."
        )

    if any(x.isspace() for x in token):
        raise TokenValidationError(
            f"Token can't contain spaces."
        )

    return True