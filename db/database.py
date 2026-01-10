from sqlmodel import SQLModel, Session, create_engine
from core.config import DATABASE_URL

engine = create_engine(DATABASE_URL) if DATABASE_URL else None

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    if engine:
        SQLModel.metadata.create_all(engine)