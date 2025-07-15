from fastapi import FastAPI, HTTPException, Depends
import uvicorn
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select
from pydantic import BaseModel, Field
from datetime import date
from typing import Annotated

app = FastAPI()
engine = create_async_engine('sqlite+aiosqlite:///books.db')
new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

class Base(DeclarativeBase):
    pass

class BookModel(Base):
    __tablename__ = "books"

    id:Mapped[int] = mapped_column(primary_key=True)
    title:Mapped[str]
    author:Mapped[str]
    date:Mapped[date]

@app.get("/setupDB")
async def SetupDB():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

class NewBook(BaseModel):
    title:str
    author:str
    date:date

class BookSchema(NewBook):
    id:int

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
    return result.scalars().all()

if __name__ == "__main__": 
    uvicorn.run("main:app", reload=True)