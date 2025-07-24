from typing import Annotated, Optional
from fastapi import Form
from pydantic import BaseModel
from datetime import datetime

class Book(BaseModel):
    title:str
    author:str
    description:Optional[str] = None

class NewBookSchema(Book):
    pass

class BookResponse(Book):
    id: int
    file_path: str
    file_type: str
    upload_date: datetime
    thumbnail_path: Optional[str] = None
    
    class Config:
        from_atributes = True