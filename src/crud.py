from sqlalchemy.orm import Session
from models.mainModels import *
from schemas import *
from sqlalchemy.ext.asyncio import AsyncSession

def get_book(session: Session, book_id: int):
    return session.query(BookModel).filter(BookModel.id == book_id).first()

def get_books(session: Session, skip: int = 0, limit: int = 100):
    return session.query(BookModel).offset(skip).limit(limit).all()

async def create_book(session: AsyncSession, file_path: str, file_type: str, data: NewBookSchema):
    db_book = BookModel(
        title = data.title,
        author = data.author,
        description = data.description,
        file_path=file_path,
        file_type=file_type
    )
    session.add(db_book)
    session.commit
    return db_book
