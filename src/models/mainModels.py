from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date

class Base(DeclarativeBase):
    pass

class BookModel(Base):
    __tablename__ = "books"

    id:Mapped[int] = mapped_column(primary_key=True)
    title:Mapped[str]
    author:Mapped[str]
    date:Mapped[date]

class UserModel(Base):
    __tablename__ = "users"

    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(unique=True)
    password:Mapped[str]