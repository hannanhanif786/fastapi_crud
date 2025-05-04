import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from decouple import config
from typing import Annotated
from user.query import get_user_email
from db import SessionDep
from models import Token, User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = config("SECRET_KEY", "")
ALGORITHM = config("ALGORITHM", "")
ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

router = APIRouter()


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate(session, email, password):

    user = get_user_email(session, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    user_data = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    token_data = {"exp": expire}
    user_data.update(token_data)
    encoded_jwt = jwt.encode(user_data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
) -> Token:
    user = authenticate(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"email": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


async def get_current_user(
    session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        if email is None:
            raise credentials_exception
        # token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user_email(session, email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_accountant_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.role.value != "accountant":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This user does not have permission to perform this action",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return current_user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
