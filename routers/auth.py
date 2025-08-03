import os
from datetime import timedelta, datetime, timezone
# from http.client import HTTPException

from fastapi import APIRouter, Depends, HTTPException,Request
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Annotated

from starlette import status

from TodoApp.database import SessionLocal
from TodoApp.models import Users
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates

# from main import templates

# SECRET_KEY =  os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

def get_secret_key():
    return os.getenv("JWT_SECRET_KEY")

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# Create a CryptContext for hashing passwords
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# This is the URL where the token will be requested
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/get-token")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

templates = Jinja2Templates(directory="TodoApp/templates")

#### Pages ####
@router.get("/login-page", response_class=templates.TemplateResponse, status_code=status.HTTP_200_OK)
def render_login_page(request: Request):
    """
    Render the login page.
    """
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register-page", response_class=templates.TemplateResponse, status_code=status.HTTP_200_OK)
def render_register_page(request: Request):
    """
    Render the registration page.
    """
    return templates.TemplateResponse("register.html", {"request": request})

#### Endpoints ####
# Function to authenticate the user
def authenticate_user(username: str, password: str, db: Session):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user
# Function to create a JWT access token
def create_access_token(username:str, user_id: str, role: str, expires_delta: timedelta):
    encode = {"sub": username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, get_secret_key(), algorithm=ALGORITHM)

# Dependency to get the current user from the token
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise JWTError
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    return {"username": username, "id": user_id, "role": user_role}

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str

class UserResponse(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    hashed_password: str
    role: str
    is_active: bool

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

@router.post("/create_user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUserRequest, db: db_dependency):
    # hash the password and save the user to the database
    new_user = Users(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=bcrypt_context.hash(user.password),  # In a real application, hash the password here
        role=user.role,
        is_active=True  # Default to active
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# This endpoint is used to get the access token for the user
@router.post("/get-token", status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def get_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                           db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    # generate a JWT token here
    jwt_token = create_access_token(user.username, user.id, user.role, timedelta(minutes=30))
    return TokenResponse(access_token=jwt_token, token_type="bearer")

# {
#   "username": "ys",
#   "email": "ys@gmail.com",
#   "first_name": "YASA",
#   "last_name": "AMS",
#   "password": "derv##44",
#   "role": "user"
# }
# {
#   "username": "ysdddf",
#   "email": "y@gcg",
#   "first_name": "yha",
#   "last_name": "sah",
#   "password": "ws34*&",
#   "role": "admin"
# }
#"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ5c2RkZGYiLCJpZCI6MSwiZXhwIjoxNzUzODU2Nzk3fQ.o5-q4FgNM4lZTPkeQASV4QfnCc_8g6fsYReCizuZAQs"
# "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ5c2RkZGYiLCJpZCI6MSwiZXhwIjoxNzUzODU2OTg3fQ.9D22xjPRR7brprLEbA2f5yjlMdYC_y1Gbi3rlV1f-Pc"

# @router.get("/auth/")
# async def get_user():
#     return {"message": "User authenticated successfully"}
