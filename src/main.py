from fastapi import FastAPI, HTTPException, Depends, Request
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
from models.mainModels import BookModel, Base
import os
from pathlib import Path

# print(f"Current working directory: {os.getcwd()}")
# print(f"Template directory exists: {os.path.exists('src/templates')}")
# print(f"Index.html exists: {os.path.exists('src/templates/index.html')}")

app = FastAPI()
engine = create_async_engine('sqlite+aiosqlite:///src/books.db')
new_session = async_sessionmaker(engine, expire_on_commit=False, autocommit=False)

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

@app.get('/SetupDB')
async def SetupDB():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

@app.get('/', response_class=HTMLResponse)
async def index(request: Request, session: SessionDep):
    query = select(BookModel)
    result = await session.execute(query)
    books = [BookResponse.model_validate(book) for book in result.scalars().all()]
    return templates.TemplateResponse("index.html", {"request": request, "result":books})

@app.post('/books')
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