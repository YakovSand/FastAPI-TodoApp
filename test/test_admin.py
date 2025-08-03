from TodoApp.test.utils import *
from TodoApp.routers.admin import get_current_user, get_db
from TodoApp.models import Todos
# from TodoApp.database import get_db
from fastapi import status, HTTPException
# Apply the override
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_all_todos(test_todo):
    response = client.get("/admin/todos")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)  # Assuming the response is a list of todos
    assert len(response.json()) > 0  # Assuming there is at least one todo in the test database

def test_delete_todo(test_todo):
    response = client.delete("/admin/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify the todo is deleted
    response = client.get("/todos/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo id:1 not found for user 1"}  # Adjust based on your error handling

def test_delete_todo_not_found():
    response = client.delete("/admin/todo/999")  # Assuming 999 does not exist
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}



