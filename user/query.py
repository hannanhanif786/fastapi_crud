from sqlalchemy.exc import NoResultFound
from sqlmodel import select
from models import User


def get_user_email(session, email):
    user = select(User).where(User.email == email)
    try:
        user_session = session.exec(user).one()
        return user_session
    except NoResultFound:
        return None
