from contextlib import asynccontextmanager
from fastapi import FastAPI, Form, HTTPException, Depends, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from jinja2 import Template
import uvicorn
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select
from pydantic import BaseModel, Field
from datetime import date
from typing import Annotated
from models.mainModels import *
from pathlib import Path
from authx import AuthX, AuthXConfig, TokenPayload

engine = create_async_engine('sqlite+aiosqlite:///src/books.db')
new_session = async_sessionmaker(engine, expire_on_commit=False, autocommit=False)

@asynccontextmanager
async def lifespan(app: FastAPI): #Startup/shutdown code
    # Startup code
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized")
    yield
    # Shutdown code would go here
    print("Application shutting down")

app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="src/templates") #Обьявляется путь к templates 

BASE_DIR = Path(__file__).parent #схраняем путь до папки static
app.mount(path="/static", app=StaticFiles(directory=BASE_DIR / "static"), name="static") #Обьявляется static

async def get_session():
    async with new_session() as session:        
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

class NewBook(BaseModel):
    title:str
    author:str
    date:date

class BookSchema(NewBook):
    id:int

class BookResponse(BaseModel):
    id:int
    title:str
    author:str
    date:date

    class Config:
        from_attributes = True

class UserLoginModel(BaseModel):
    username:str
    password:str

config = AuthXConfig()
config.JWT_SECRET_KEY = "mysecretkey"
config.JWT_ACCESS_COOKIE_NAME = "accesstoken"
config.JWT_TOKEN_LOCATION = ["cookies"]

security = AuthX(config=config)

@app.get('/', response_class=HTMLResponse)
async def index(request: Request, session: SessionDep):
    query = select(BookModel)
    result = await session.execute(query)
    books = [BookResponse.model_validate(book) for book in result.scalars().all()]
    return templates.TemplateResponse("index.html", {"request": request, "result":books})

@app.post('/', response_class=HTMLResponse)
async def index_post(request: Request, session: SessionDep, search: Annotated[str,Form()]):
    if not search:
        query = select(BookModel)
    else:
        query = select(BookModel).filter(BookModel.title.contains(search))
    result = await session.execute(query)
    books = [BookResponse.model_validate(book) for book in result.scalars().all()]
    return templates.TemplateResponse("index.html", {"request": request, "result":books})

@app.post('/register')
async def register(session:SessionDep, data:UserLoginModel):
    new_user = UserModel(
        name = data.username,
        password = data.password
    )
    session.add(new_user)
    await session.commit()
    return {"success":True, "message":"User "+data.username+" added"}

@app.post('/login')
async def login(responce:Response ,session:SessionDep, cred:UserLoginModel):
    user_result = await session.execute(select(UserModel).filter_by(name=cred.username))
    user = user_result.scalars().first()

    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    if user.password == cred.password:
        token = security.create_access_token(uid=str(user.id))
        responce.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
        return {"access_token": token}
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")


@app.post('/books', dependencies=[Depends(security.access_token_required)])
async def create_book(data: NewBook, session: SessionDep):
    new_book = BookModel(
        title=data.title,
        author=data.author,
        date=data.date,
    )
    session.add(new_book)
    await session.commit()
    return {"success": True, "message": "Book "+data.title+" added"}

@app.get('/books')
async def get_books(session: SessionDep):
    query = select(BookModel)
    result = await session.execute(query)
    # print (result.scalars().all())
    return result.scalars().all()

if __name__ == "__main__": 
    uvicorn.run("main:app", reload=True)