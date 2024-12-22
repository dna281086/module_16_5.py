from fastapi import FastAPI, Path, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from typing import Annotated

app = FastAPI()
templates = Jinja2Templates(directory="Templates")

users = []


class User(BaseModel):
    id: int
    username: str
    age: int


@app.get("/", response_class=HTMLResponse)
async def get_all_users(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("users.html", {"request": request, "users": users})


@app.get("/users/{user_id}", response_class=HTMLResponse)
async def get_one_user(request: Request, user_id: int) -> HTMLResponse:
    if user_id < 0 or user_id >= len(users):
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("users.html", {"request": request, "user": users[user_id]})


@app.post("/user/{username}/{age}", response_model=str)
async def create_user(user: User,
                      username: Annotated[str, Path(min_length=1, max_length=20, description="Enter username")],
                      age: int = Path(ge=1, le=100, description="Enter age")) -> str:
    if users:
        user_id = max(user.id for user in users) + 1
    else:
        user_id = 1
    user.id = user_id
    user.username = username
    user.age = age
    users.append(user)
    return f"User {user_id} is registered"


@app.put("/user/{user_id}/{user_name}/{age}", response_model=str)
async def update_user(username: Annotated[str, Path(min_length=1, max_length=20, description="Enter username")],
                      age: int = Path(ge=1, le=100, description="Enter age"), user_id: int = Path(ge=0)) -> str:
    for existing_user in users:
        if existing_user.id == user_id:
            existing_user.username = username
            existing_user.age = age
            return f"The user {user_id} is updated"
    raise HTTPException(status_code=404, detail="Пользователь не найден")


@app.delete('/user/{user_id}')
def delete_user(user_id: int) -> str:
    for i, user in enumerate(users):
        if user.id == user_id:
            return users.pop(i)
    else:
        raise HTTPException(status_code=404, detail='Пользователя не найден')
