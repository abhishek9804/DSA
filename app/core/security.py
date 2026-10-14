from datetime import datetime, timedelta, timezone
from uuid import UUID
import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from app.core.config import settings

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password( plain_password: str, stored_password_hash: str):

    return password_hash.verify(
        plain_password,
        stored_password_hash,
    )

def create_access_token(user_id: UUID) ->str:
    now = datetime.now(timezone.utc)
    
    expires_at = now + timedelta(
        minutes = settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": expires_at
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algoritm,
    )

def decode_access_token(token: str) -> UUID:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algoritm],
        )

        if payload.get("type") != "access":
            raise ValueError("Invalid token type")
        
        subject = payload.get("sub")

        if not subject:
            raise ValueError("Token subject is missing")
        
        return UUID(subject)
    except (InvalidTokenError, ValueError) as error:
        raise ValueError("Invalid or expired access token") from error
