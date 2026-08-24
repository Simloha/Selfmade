# /backend/auth.py
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext

# Cryptographic configuration keys
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-for-local-dev-only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hardcoded production access dictionary (Swap with an encrypted database connection in live production)
USER_DATABASE = {
    "kryptera_operator": pwd_context.hash("QuantSecurePass2026!")
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str) -> Optional[str]:
    if username in USER_DATABASE:
        if verify_password(password, USER_DATABASE[username]):
            return username
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
