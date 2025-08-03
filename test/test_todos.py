from fastapi import status, HTTPException
from TodoApp.routers.todos import  get_current_user
from TodoApp.database import get_db
from TodoApp.test.utils import *


# Apply the override
app.dependency_overrides[get_db] = override_get_db

app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo):
    print("Test get_db id:", id(get_db))
    print("Test get_current_user id:", id(get_current_user))
    print("Test app id:", id(app))
    response = client.get("/todos/")
    for route in app.routes:
        print(route.path)
    print("STATUS:", response.status_code)
    print("BODY:", response.text)
    assert response.status_code == status.HTTP_200_OK
    print("=====")
    # assert response.json() == []  # Assuming no todos are present in the test database
    assert response.json() == [{'title':'Test Todo', 'description':'This is a test todo item', 'priority':1,
                                'complete':False, 'owner_id':1, 'id':1}]  # Adjust based on your test data


def test_read_one_authenticated(test_todo):
    response = client.get("/todos/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'title':'Test Todo', 'description':'This is a test todo item', 'priority':1,
                                'complete':False, 'owner_id':1, 'id':1}


def test_read_one_not_authenticated():
    response = client.get("/todos/99")
    with pytest.raises(HTTPException) as exc_info:
        # Call the function directly that raises HTTPException
        raise HTTPException(status_code=404, detail="Todo id:99 not found for user 1")
    assert response.status_code == 404

    assert exc_info.value.detail == "Todo id:99 not found for user 1"


def test_create_todo(test_todo):
    todo_data = {
        "title": "New Todo",
        "description": "This is a new todo item",
        "priority": 2,
        "complete": False
    }
    response = client.post("/todos/", json=todo_data)
    assert response.status_code == status.HTTP_201_CREATED
    created_todo = response.json()
    assert created_todo['todo']['title'] == todo_data['title']
    assert created_todo['todo']['description'] == todo_data['description']
    assert created_todo['todo']['priority'] == todo_data['priority']
    assert created_todo['todo']['complete'] == todo_data['complete']


def test_update_todo(test_todo):
    update_data = {
        "title": "Updated Todo",
        "description": "This is an updated todo item",
        "priority": 3,
        "complete": True
    }
    response = client.put("/todos/1", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    updated_todo = response.json()
    assert updated_todo['todo']['title'] == update_data['title']
    assert updated_todo['todo']['description'] == update_data['description']
    assert updated_todo['todo']['priority'] == update_data['priority']
    assert updated_todo['todo']['complete'] == update_data['complete']


def test_delete_todo(test_todo):
    response = client.delete("/todos/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify the todo is deleted
    response = client.get("/todos/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo id:1 not found for user 1"}