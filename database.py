import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

def get_db_url():
    if "DB_URL" not in os.environ:
        raise ValueError("Environment variable 'DB_URL' is not set.")
    return os.getenv("DB_URL")


SQLALCHEMY_DATABASE_URL = get_db_url()
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Uncomment the following lines to use SQLite instead of PostgreSQL
# SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    print("original get_db called")
    try:
        yield db
    finally:
        db.close()