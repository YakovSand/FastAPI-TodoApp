from TodoApp.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)  # Default is_active to True
    role = Column(String)
    phone_number = Column(String(15), nullable=True)


class Todos(Base):
    __tablename__ = "todosapp"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    priority = Column(Integer, default=1)  # Default priority is 1
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))  # Foreign key to Users table, assuming user ID is an integer
