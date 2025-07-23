from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    pass

class BookModel(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    description = Column(Text, nullable=True)
    file_path = Column(String)
    file_type = Column(String)  # Only pdf and docx for now
    upload_date = Column(DateTime, default=datetime.now)
    thumbnail_path = Column(String, nullable=True) # Book covers

class UserModel(Base):
    __tablename__ = "users"

    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(unique=True)
    password:Mapped[str]