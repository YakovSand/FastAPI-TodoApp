import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text, StaticPool
from sqlalchemy.orm import sessionmaker

from TodoApp.database import Base
from TodoApp.main import app
from TodoApp.models import Todos, Users
from TodoApp.routers.auth import bcrypt_context

print(Base.metadata.tables)  # This should now show your tables

BASE_DIR = os.path.dirname(__file__)  # This will always point to the current script's folder

# create fake data for testing
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'test_todosapp.db')}"

engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       connect_args={"check_same_thread": False},
                       poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)
with engine.connect() as conn:
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
    tables = result.fetchall()
    print("Tables in DB:", tables)


def override_get_current_user():
    return {'id': 1, 'username': 'testuser', 'role': 'admin'}


# Override dependency
def override_get_db():
    print("override_get_db called")
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


client = TestClient(app)


@pytest.fixture
def test_todo():
    # Create a test todo item
    todo = Todos(title="Test Todo", description="This is a test todo item", priority=1, complete=False, owner_id=1)
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todosapp;"))
        connection.commit()


@pytest.fixture(autouse=True)
def test_user():
    # Create a test user
    user = Users(
        username="testuser",
        email="tst@gmail.com",
        first_name="Test",
        last_name="User",
        hashed_password=bcrypt_context.hash("testpassword"),
        is_active=True,
        role="admin"
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()


@pytest.fixture(scope="session", autouse=True)
def set_test_env_vars():
    os.environ["JWT_SECRET_KEY"] = "test-secret"