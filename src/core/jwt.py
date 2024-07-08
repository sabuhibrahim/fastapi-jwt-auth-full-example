import uuid
import sys
from datetime import timedelta, datetime, timezone

from jose import jwt, JWTError
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

from . import config
from src.schemas import User, TokenPair, JwtTokenSchema
from src.exceptions import AuthFailedException
from src.models import BlackListToken


REFRESH_COOKIE_NAME = "refresh"
SUB = "sub"
EXP = "exp"
IAT = "iat"
JTI = "jti"

def _get_utc_now():
    if sys.version_info >= (3, 2):
        # For Python 3.2 and later
        current_utc_time = datetime.now(timezone.utc)
    else:
        # For older versions of Python
        current_utc_time = datetime.utcnow()
    return current_utc_time

def _create_access_token(payload: dict, minutes: int | None = None) -> JwtTokenSchema:
    expire = _get_utc_now() + timedelta(
        minutes=minutes or config.ACCESS_TOKEN_EXPIRES_MINUTES
    )

    payload[EXP] = expire

    token = JwtTokenSchema(
        token=jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM),
        payload=payload,
        expire=expire,
    )

    return token


def _create_refresh_token(payload: dict) -> JwtTokenSchema:
    expire = _get_utc_now() + timedelta(minutes=config.REFRESH_TOKEN_EXPIRES_MINUTES)

    payload[EXP] = expire

    token = JwtTokenSchema(
        token=jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM),
        expire=expire,
        payload=payload,
    )

    return token


def create_token_pair(user: User) -> TokenPair:
    payload = {SUB: str(user.id), JTI: str(uuid.uuid4()), IAT: _get_utc_now()}

    return TokenPair(
        access=_create_access_token(payload={**payload}),
        refresh=_create_refresh_token(payload={**payload}),
    )


async def decode_access_token(token: str, db: AsyncSession):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        black_list_token = await BlackListToken.find_by_id(db=db, id=payload[JTI])
        if black_list_token:
            raise JWTError("Token is blacklisted")
    except JWTError:
        raise AuthFailedException()

    return payload


def refresh_token_state(token: str):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
    except JWTError as ex:
        print(str(ex))
        raise AuthFailedException()

    return {"token": _create_access_token(payload=payload).token}


def mail_token(user: User):
    """Return 2 hour lifetime access_token"""
    payload = {SUB: str(user.id), JTI: str(uuid.uuid4()), IAT: _get_utc_now()}
    return _create_access_token(payload=payload, minutes=2 * 60).token


def add_refresh_token_cookie(response: Response, token: str):
    exp = _get_utc_now() + timedelta(minutes=config.REFRESH_TOKEN_EXPIRES_MINUTES)
    exp.replace(tzinfo=timezone.utc)

    response.set_cookie(
        key="refresh",
        value=token,
        expires=int(exp.timestamp()),
        httponly=True,
    )
