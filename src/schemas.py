from typing import Annotated, Optional
from fastapi import Form
from pydantic import BaseModel
from datetime import date

class Book(BaseModel):
    title:str
    author:str
    description:Optional[str] = None

class NewBookSchema(Book):
    pass

class BookResponse(BaseModel):
    id:int
    title:str
    author:str
    date:date

    class Config:
        from_attributes = True

class UserLoginModel(BaseModel):
    username:Annotated[str, Form()]
    password:Annotated[str, Form()]