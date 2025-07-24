from sqlalchemy import select
from sqlalchemy.orm import Session
from models.mainModels import *
from schemas import *
from sqlalchemy.ext.asyncio import AsyncSession

async def get_book(session: AsyncSession, book_id: int):
    # return session.query(BookModel).filter(BookModel.id == book_id).first()
    query = select(BookModel).where(BookModel.id == book_id)
    result = await session.execute(query)
    result = result.scalars().all()
    return result

async def get_books(session: AsyncSession, skip: int = 0, limit: int = 100):
    # return session.query(BookModel).offset(skip).limit(limit).all()
    return select(BookModel).offset(skip).limit(limit)

async def create_book(session: AsyncSession, file_path:str, file_type:str, data: NewBookSchema):
    db_book = BookModel(
        title = data.title,
        author = data.author,
        description = data.description,
        file_path=file_path,
        file_type=file_type
    )
    session.add(db_book)
    await session.commit()
    return db_book
