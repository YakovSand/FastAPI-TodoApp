from TodoApp.test.utils import *
from TodoApp.models import Users
from TodoApp.routers.users import get_current_user, get_db
from fastapi import status, HTTPException

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_user_info(test_user):
    response = client.get("/users/get-user")
    assert response.status_code == status.HTTP_200_OK
    user_info = response.json()

    assert user_info['id'] == test_user.id
    assert user_info['username'] == test_user.username
    assert user_info['role'] == test_user.role
    assert user_info['password'] == test_user.hashed_password
    assert user_info['phone_number'] == test_user.phone_number



