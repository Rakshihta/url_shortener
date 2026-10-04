import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi.security import HTTPAuthorizationCredentials
from database import get_db
from models import User

load_dotenv()
_password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET_KEY = os.getenv("SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password must not be empty")
    return _password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _password_context.verify(plain_password, hashed_password)


def create_access_token(data:dict) ->str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,JWT_SECRET_KEY,algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    if not JWT_SECRET_KEY:
        raise RuntimeError("Set the JWT_SECRET_KEY environment variable")
    try:
        claims = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None
    if not claims.get("sub"):
        return None
    return claims


from fastapi.security import HTTPBearer

optional_scheme = HTTPBearer(auto_error=False)

def get_current_user_optional(
    token: HTTPAuthorizationCredentials = Depends(optional_scheme),
    db: Session = Depends(get_db)
):
    # 1. if token is None, return None immediately (no credentials given — that's fine here)
    if token is None:
        return None
    else:

        try:
            payload = jwt.decode(token.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        else:
            user = db.query(User).filter(User.id==int(user_id)).first()
            return user
    