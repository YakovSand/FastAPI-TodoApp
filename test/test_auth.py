import os
import pytest
from TodoApp.test.utils import *
from TodoApp.routers.auth import authenticate_user, get_db, create_access_token, get_secret_key, ALGORITHM, get_current_user
from fastapi import status, HTTPException
from jose import jwt
from datetime import timedelta

# Apply the override

app.dependency_overrides[get_db]  = override_get_db


def test_authenticate_user(test_user):
    db = TestingSessionLocal()
    authenticated_user = authenticate_user(test_user.username, "testpassword", db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username
    non_existent_user = authenticate_user("nonexistent", "wrongpassword", db)
    assert non_existent_user is False

    wrong_password_user = authenticate_user(test_user.username, "wrongpassword", db)
    assert wrong_password_user is False



    # # Test with valid credentials
    # response = client.post("/auth/login", json={"username": "testuser", 'testpassword': "testpassword"})
    # assert response.status_code == status.HTTP_200_OK
    # assert "access_token" in response.json()
    # assert response.json()["token_type"] == "bearer"
    #
    # # Test with invalid credentials
    # response = client.post("/auth/login", json={"username": "wronguser", "password": "wrongpassword"})
    # assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # assert response.json() == {"detail": "Invalid credentials"}

def test_create_access_token(test_user):
    db = TestingSessionLocal()
    user = authenticate_user(test_user.username, "testpassword", db)
    assert user is not False

    # Assuming create_access_token is a function that generates a JWT token
    jwt_token = create_access_token(user.username, user.id, user.role, timedelta(minutes=30))
    assert jwt_token is not None

    decoded_token = jwt.decode(jwt_token, get_secret_key(), algorithms=[ALGORITHM], options={"verify_signature": False})
    assert decoded_token["sub"] == user.username

    # # Test with invalid credentials
    # jwt_token_invalid = create_access_token("invaliduser", "999", "invalidrole", timedelta(minutes=30))
    # assert jwt_token_invalid is None

@pytest.mark.asyncio
async def test_get_current_user(test_user):

    jwt_token = create_access_token(test_user.username, test_user.id, test_user.role, timedelta(minutes=30))

    user = await get_current_user(jwt_token)
    assert user["username"] == test_user.username
    assert user["id"] == test_user.id
    assert user["role"] == test_user.role