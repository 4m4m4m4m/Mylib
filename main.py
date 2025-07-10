from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel, Field

app = FastAPI()

books = [
    {
        "id":1,
        "title":"async in python",
        "autor":"Some dude"
    },
    {
        "id":2,
        "title":"async in python 2",
        "autor":"Same dude"
    },
]

@app.get("/books")
def read_books():
    return books

@app.get("/books/{book_id}")
def read_book(book_id:int):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

class NewBook(BaseModel):
    title:str
    author:str = Field()

@app.post('/books')
def create_book(new_book: NewBook):
    books.append({
        "id":len(books)+1,
        "title": new_book.title,
        "author": new_book.author,
    })
    return {"success": True, "message":"Book "+new_book.title+" added"}


if __name__ == "__main__": 
    uvicorn.run("main:app", reload=True)