import uuid
from datetime import timedelta, datetime
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from . import config
from src.schemas import User, TokenPair, JwtTokenSchema
from src.exceptions import AuthFailedException
from src.models import BlackListToken


def _create_access_token(payload: dict, minutes: int | None = None) -> JwtTokenSchema:
    expire = datetime.utcnow() + timedelta(
        minutes=minutes or config.ACCESS_TOKEN_EXPIRES_MINUTES
    )

    payload["exp"] = expire
    payload["frs"] = False

    token = JwtTokenSchema(
        token=jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM),
        payload=payload,
        expire=expire,
    )

    return token


def _create_refresh_token(payload: dict) -> JwtTokenSchema:
    expire = datetime.utcnow() + timedelta(minutes=config.REFRESH_TOKEN_EXPIRES_MINUTES)

    payload["exp"] = expire
    payload["frs"] = True

    token = JwtTokenSchema(
        token=jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM),
        expire=expire,
        payload=payload,
    )

    return token


def create_token_pair(user: User) -> TokenPair:
    payload = {"sub": str(user.id), "name": user.full_name, "jti": str(uuid.uuid4())}

    return TokenPair(
        access=_create_access_token(payload={**payload}),
        refresh=_create_refresh_token(payload={**payload}),
    )


async def decode_access_token(token: str, db: AsyncSession):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if payload.get("frs"):
            raise JWTError("Access token need")
        black_list_token = await BlackListToken.find_by_id(db=db, id=payload["jti"])
        if black_list_token:
            raise JWTError("Token is blacklisted")
    except JWTError:
        raise AuthFailedException()

    return payload


def refresh_token_state(token: str):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if not payload.get("frs"):
            raise JWTError("Refresh token need")
    except JWTError as ex:
        print(str(ex))
        raise AuthFailedException()

    return {"access": _create_access_token(payload=payload).token}


def mail_token(user: User):
    """Return 2 hour lifetime access_token"""
    payload = {"sub": str(user.id), "name": user.full_name, "jti": str(uuid.uuid4())}
    return _create_access_token(payload=payload, minutes=2 * 60).token
