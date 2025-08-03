from fastapi import APIRouter, HTTPException, Path, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from typing_extensions import Annotated

from TodoApp.database import SessionLocal
from TodoApp.models import Todos
from TodoApp.routers.auth import get_current_user


router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# This will inject the database session into the route handlers
db_dependency = Annotated[Session, Depends(get_db)]
# This will inject the current user into the route handlers
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/todos", status_code=status.HTTP_200_OK)
async def get_all_todos(user: user_dependency, db: db_dependency):
    if user is None or user['role'] != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    todos = db.query(Todos).all()
    return todos

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo( db: db_dependency,
                       user: user_dependency,
                       todo_id: int = Path(gt=0)):
    if user is None or user['role'] != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted successfully"}