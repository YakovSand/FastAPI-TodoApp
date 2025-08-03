from fastapi import APIRouter, HTTPException, Path, Depends, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from typing_extensions import Annotated

from TodoApp.database import SessionLocal
from TodoApp.models import Todos
from TodoApp.routers.auth import get_current_user
from TodoApp.database import get_db
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

# from TodoApp.main import templates

templates = Jinja2Templates(directory="TodoApp/templates")


class TodosRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Title of the todo item")
    description: str = Field(..., min_length=1, max_length=500, description="Description of the todo item")
    priority: int = Field(ge=1, le=10, description="Priority of the todo item (1-10)", default=1)
    complete: bool = Field(default=False, description="Completion status of the todo item")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, Bread, Eggs",
                "priority": 2,
                "complete": False
            }
        }
    }

def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response

class UsersRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username of the user")
    email: str = Field(..., min_length=5, max_length=100, description="Email of the user")
    first_name: str = Field(..., min_length=1, max_length=50, description="First name of the user")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name of the user")
    hashed_password: str = Field(..., min_length=8, max_length=100, description="Hashed password of the user")
    is_active: bool = Field(default=True, description="Is the user active?")
    role: str = Field(..., min_length=1, max_length=20, description="Role of the user")

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "johndoe",
                "email": "user@mail.vb",
                "first_name": "John",
                "last_name": "Doe",
                "hashed_password": "hashedpassword123",
                "is_active": True,
                "role": "admin"
            }
        }
    }


router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)


# def get_db():
#     db = SessionLocal()
#     print("original get_db called")
#     try:
#         yield db
#     finally:
#         db.close()

# This will inject the database session into the route handlers
db_dependency = Annotated[Session, Depends(get_db)]
# This will inject the current user into the route handlers
user_dependency = Annotated[dict, Depends(get_current_user)]

#### Pages ####
@router.get("/todo-page")
async def render_todos_page(request: Request, db: db_dependency):
    """
    Render the Todos home page.
    """
    try:
        user = await get_current_user(request.cookies.get("access_token"))

        if user is None:
            return redirect_to_login()

        todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()


        return templates.TemplateResponse(name ="todo.html",context= {"request": request, "todos": todos, "user": user})
    except:
        return redirect_to_login()

@router.get("/add-todo-page")
async def render_add_todo_page(request: Request):
    """
    Render the Add Todo page.
    """
    try:
        user = await get_current_user(request.cookies.get("access_token"))

        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse(name="add-todo.html", context={"request": request, "user": user})
    except:
        return redirect_to_login()

@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, db: db_dependency, todo_id: int = Path(gt=0)):
    """
    Render the Edit Todo page.
    """
    try:
        user = await get_current_user(request.cookies.get("access_token"))

        if user is None:
            return redirect_to_login()

        todo = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user.get("id")).first()
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")

        return templates.TemplateResponse(name="edit-todo.html", context={"request": request, "todo": todo, "user": user})
    except:
        return redirect_to_login()



#### API Endpoints ####
@router.get("/")
def read_all(user: user_dependency,db: db_dependency):  # dependency injection to get the database session
    print("!!!User:", user)
    print("Router get_db id:", id(get_db))
    print("Router get_current_user id:", id(get_current_user))
    print("Router or App id:", id(router))
    todos = db.query(Todos).filter(Todos.owner_id == user['id']).all()
    return todos
# @router.get("/", status_code=status.HTTP_200_OK)
# async def read_all(user: user_dependency, db: db_dependency):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     print("!!!User:", user)
#     return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo_by_id(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = user['id']
    todo = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user_id).first()
    if todo:
        return todo
    raise HTTPException(status_code=404, detail="Todo id:" + str(todo_id) + " not found for user " + str(user_id))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_todo(todo_request: TodosRequest, user: user_dependency, db: db_dependency):
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        new_todo = Todos(**todo_request.model_dump(), owner_id=user['id'])
        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)
        return {"message": "Todo added successfully", "todo": new_todo}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding todo: {str(e)}")


@router.put("/{todo_id}", status_code=status.HTTP_200_OK)
async def update_todo(todo_request: TodosRequest,
                      user: user_dependency,
                      db: db_dependency,
                      todo_id: int = Path(gt=0)):
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        user_id = user['id']
        todo = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user_id).first()
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")

        for key, value in todo_request.model_dump().items():
            setattr(todo, key, value)

        db.commit()
        db.refresh(todo)
        return {"message": "Todo updated successfully", "todo": todo}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating todo: {str(e)}")


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, user: user_dependency, todo_id: int = Path(gt=0)):
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        user_id = user['id']
        todo = db.query(Todos).filter(Todos.id == todo_id,  Todos.owner_id == user_id).first()
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")

        db.delete(todo)
        db.commit()
        return {"message": "Todo deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting todo: {str(e)}")
