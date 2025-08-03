from typing import Optional

from fastapi import APIRouter, HTTPException, Path, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from typing_extensions import Annotated

from TodoApp.database import SessionLocal
from TodoApp.models import Todos, Users
from TodoApp.routers.auth import get_current_user, bcrypt_context

router = APIRouter(
    prefix="/users",
    tags=["users"]
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

class UserInfoResponse(BaseModel):
    id: int
    username: str
    role: str
    password: str
    phone_number: Optional[str] = None



@router.get("/get-user", status_code=status.HTTP_200_OK, response_model=UserInfoResponse)
async def get_user_info(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user_id = user['id']
    user_info = db.query(Users).filter(Users.id == user_id).first()

    if not user_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserInfoResponse(
        id=user_info.id,
        username=user_info.username,
        role=user_info.role,
        password = user_info.hashed_password,
        phone_number = user_info.phone_number
    )

@router.put("/update-password", status_code=status.HTTP_200_OK, response_model=UserInfoResponse)
async def update_password(new_password: str, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user_id = user['id']
    user_info = db.query(Users).filter(Users.id == user_id).first()

    if not user_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update the user's password
    user_info.hashed_password = bcrypt_context.hash(new_password)
    db.commit()

    return UserInfoResponse(
        id=user_info.id,
        username=user_info.username,
        role=user_info.role,
        password=user_info.hashed_password,
        phone_number=user_info.phone_number
    )

@router.put("/update-phone-number", status_code=status.HTTP_200_OK, response_model=UserInfoResponse)
async def update_phone_number(new_phone_number: str, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user_id = user['id']
    user_info = db.query(Users).filter(Users.id == user_id).first()

    if not user_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update the user's phone number
    user_info.phone_number = new_phone_number
    db.commit()

    return UserInfoResponse(
        id=user_info.id,
        username=user_info.username,
        role=user_info.role,
        password=user_info.hashed_password,
        phone_number=user_info.phone_number
    )