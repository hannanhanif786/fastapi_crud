from fastapi import APIRouter, HTTPException, status
from db import SessionDep
from models import UserBase, UserCreate, User, UserUpdate
from user import get_user_email
from auth import get_password_hash

router = APIRouter()


@router.get("/user-by-email")
async def get_user_info(session: SessionDep, email: str) -> UserBase:
    user = get_user_email(session, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not Found")
    return UserBase.from_orm(user)


@router.post("/create-user")
def create_user(session: SessionDep, user: UserCreate) -> UserBase:

    current_user = get_user_email(session, user.email)
    if current_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user already exists")

    user = User(**user.dict(), hashed_password=get_password_hash(user.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.patch("/update-user")
def update_user(session: SessionDep, email: str, user: UserUpdate) -> UserBase:

    user_obj = get_user_email(session, email)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not Found")

    updated_user = user.model_dump(exclude_unset=True)
    user_obj.sqlmodel_update(updated_user)
    session.add(user_obj)
    session.commit()
    session.refresh(user_obj)
    return user_obj


@router.delete("/delete-user")
def delete_user(session: SessionDep, email: str) -> dict[str, UserBase]:

    user = get_user_email(session, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not Found")

    session.delete(user)
    session.commit()
    return {"User Deleted": user}
