import uuid
from pydantic import EmailStr
from typing import Optional
from enum import Enum
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: str = Field(max_length=30)
    is_active: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    email: EmailStr = Field(unique=True, max_length=50)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=25)


class Roles(Enum):
    accountant = "accountant"
    user = "user"


class User(UserBase, table=True):

    __tablename__ = "users"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    role: Roles = "user"


class UserUpdate(SQLModel):
    username: Optional[str] = None
    is_active: Optional[bool] = False
    is_superuser: Optional[bool] = False


class Token(SQLModel):
    access_token: str
    token_type: str
