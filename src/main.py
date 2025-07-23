from contextlib import asynccontextmanager
from fastapi import FastAPI, File, Form, HTTPException, Depends, Request, Response, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import date
from schemas import *
from utils import *
from typing import Annotated, Optional
from models.mainModels import *
from pathlib import Path
from authx import AuthX, AuthXConfig

# DB init
engine = create_async_engine('sqlite+aiosqlite:///src/books.db')
new_session = async_sessionmaker(engine, expire_on_commit=False, autocommit=False)

@asynccontextmanager
async def lifespan(app: FastAPI): # Startup/shutdown code  
    # Startup code
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized")
    yield
    # Shutdown code would go here
    print("Application shutting down")

app = FastAPI(lifespan=lifespan)

# Templates path
templates = Jinja2Templates(directory="src/templates") 

# Static path
BASE_DIR = Path(__file__).parent 
app.mount(path="/static", app=StaticFiles(directory=BASE_DIR / "static"), name="static") # Init static

async def get_session():
    async with new_session() as session:        
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

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

@app.get('/register', response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("sign-in.html", {"request": request, "title": "Please register", "method":"/register"})

@app.post('/register',)
async def register(session:SessionDep, responce:Response, username: str = Form(), password: str = Form()):
    new_user = UserModel(
        name = username,
        password = password
    )
    session.add(new_user)
    await session.commit()
    responce.headers["Location"] = "/login"
    responce.status_code = 303
    
    return responce, {"success":True, "message":"User "+username+" added"}

@app.get('/login', response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("sign-in.html", {"request": request, "title": "Please Sign in", "method":"/login"})

@app.post('/login')
async def login(responce:Response ,session:SessionDep, username: str = Form(), password: str = Form()):
    user_result = await session.execute(select(UserModel).filter_by(name=username))
    user = user_result.scalars().first()

    print(username)

    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    if user.password == password:
        token = security.create_access_token(uid=str(user.id))
        responce.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
        responce.status_code=303
        responce.headers["Location"] = "/"

        return responce
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")


@app.post('/books', dependencies=[Depends(security.access_token_required)])
async def create_book(data: Book, session: SessionDep):
    new_book = BookModel(
        title=data.title,
        author=data.author,
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

@app.post('/upload')
async def upload(
    session: SessionDep,
    title: str = Form(),
    author: str = Form(),
    desc: Optional[str] = Form(),
    file: UploadFile = File(),
):
    allowed_types = ["pdf", "docx"]
    file_type = get_file_type(str(file.filename))

    if file_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    file_path = save_uploaded_file(file)

    book_data = Book(
        title=title,
        author=author,
        description=desc
    )

    db_book = await create_book(session=session, file_path=file_path, file_type=file_type, data=book_data, )

    return db_book

    

if __name__ == "__main__": 
    uvicorn.run("main:app", reload=True)