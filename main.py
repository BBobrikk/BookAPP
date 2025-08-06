import time
from typing import Callable

import uvicorn
from fastapi import FastAPI, APIRouter, BackgroundTasks, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from httpx import Request
from sqlalchemy import select

from ObjectModels import BookModel
from TableModels import BooksORM
from Tools import *
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):

    await setup_db()

    yield


router = APIRouter(prefix="/books", tags=["Books"])

app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def request_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    finish = time.time()
    response.headers["X-REQUEST-TIME"] = str(finish - start)
    return response


@app.exception_handler(RequestValidationError)
async def unprocessable_entity_exception(req: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"Ошибка": "Недействительный формат данных"},
    )


@router.post("/add_book", summary="Добавить книгу")
async def add_book(data: BookModel, sess: SessionDep):
    sess.add(BooksORM(title=data.title, rating=data.rating))
    await sess.commit()
    return {f"Книга : {data.title}": f"Добавлена"}


@router.get("", summary="Все книги")
async def all_books(sess: SessionDep):
    query = select(BooksORM)
    res = await sess.execute(query)
    res = res.scalars().all()
    if len(res) > 0:
        return res
    raise HTTPException(status_code=404, detail="Books not found")


@router.get("/{book_id}", summary="Найти книгу")
async def get_book(book_id: int, sess: SessionDep):
    book = await sess.get(BooksORM, book_id)
    if book:
        return book
    raise HTTPException(status_code=404, detail="Книга не найдена")


@router.delete("/remove_book", summary="Удалить книгу")
async def del_book(sess: SessionDep, book_id: int):
    book = await sess.get(BooksORM, book_id)
    print(book)
    if book:
        await sess.delete(book)
        await sess.commit()
        return {f"Книга ": "удалена"}

    raise HTTPException(status_code=404, detail="Книга не найдена")


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
