import uuid
from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: str = Field(max_length=30)
    is_active: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    email: EmailStr = Field(unique=True, max_length=50)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=25)


class User(UserBase, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
