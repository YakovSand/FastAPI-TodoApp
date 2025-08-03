from fastapi import FastAPI, Request, status

from TodoApp.database import engine, Base
from TodoApp.routers import auth, todos, admin, users
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from routers.todos import redirect_to_login

app = FastAPI()

# Create the database tables if they do not exist
Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="TodoApp/templates")

app.mount("/static", StaticFiles(directory="TodoApp/static"), name="static")

@app.get("/", tags=["home"])
def read_home(request: Request):
    # return templates.TemplateResponse("home.html", {"request": request})
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)

# Health check endpoint
@app.get("/healthy", tags=["health"])
def health_check():
    return {"status": "healthy"}
# Include the routers for different functionalities
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)









