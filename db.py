from typing import Annotated
from decouple import config
from sqlmodel import Session, create_engine
from fastapi import Depends

DATABASE_URL = config("DATABASE_URL")
# "mysql+pymysql://<username>:<password>@<host>/<database_name>"

connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
