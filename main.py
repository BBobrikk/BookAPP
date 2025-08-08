import time
import uvicorn
from fastapi import FastAPI, APIRouter, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from DataBase.ObjectModels import BookModel, CredModel
from DataBase.TableModels import BooksORM, CredsORM
from Tools import *
from contextlib import asynccontextmanager
from Authorization import security
from redis import Redis


@asynccontextmanager
async def lifespan(app: FastAPI):

    await setup_db()

    yield


b_router = APIRouter(prefix="/books", tags=["Books"])
c_router = APIRouter(prefix="/auth", tags=["Auth"])

app = FastAPI(lifespan=lifespan)

client = Redis()


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


@app.exception_handler(IntegrityError)
async def unique_violation_error(req: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"Ошибка": "Нарушение уникальности"},
    )


@b_router.post("/add_book", summary="Добавить книгу")
async def add_book(data: BookModel, sess: SessionDep, request: Request, root=True):
    token = request.cookies.get("access_auth")
    if token or root:
        sess.add(BooksORM(title=data.title, rating=data.rating))
        return {f"Книга : {data.title}": f"Добавлена"}
    raise HTTPException(
        status_code=401, detail={"Статус": "Пользователь не авторизован"}
    )


@b_router.get("", summary="Все книги")
async def all_books(sess: SessionDep):
    query = select(BooksORM)
    res = await sess.execute(query)
    res = res.scalars().all()
    if len(res) > 0:
        return res
    raise HTTPException(status_code=404, detail={"Статус": "Книга не найдена"})


@b_router.get("/{book_id}", summary="Найти книгу")
async def get_book(book_id: int, sess: SessionDep):
    redis_response = client.hgetall(f"book:{book_id}")
    if redis_response == {}:
        book = await sess.get(BooksORM, book_id)
        if book:
            cache = client.hset(
                f"book:{book_id}",
                mapping={
                    "book_id": f"{book_id}",
                    "title": f"{book.title}",
                    "rating": f"{book.rating}",
                },
            )
            return book
        raise HTTPException(status_code=404, detail={"Статус": "Книга не найдена"})
    return redis_response


@b_router.delete("/remove_book", summary="Удалить книгу")
async def del_book(sess: SessionDep, book_id: int, request: Request, root=True):
    token = request.cookies.get("access_auth")
    if token or root:
        book = await sess.get(BooksORM, book_id)
        print(book)
        if book:
            await sess.delete(book)
            await sess.commit()
            return {f"Книга ": "удалена"}

        raise HTTPException(status_code=404, detail={"Статус": "Книга не найдена"})
    raise HTTPException(
        status_code=401, detail={"Статус": "Пользователь не авторизован"}
    )


@c_router.post("/registry", summary="registration")
async def registry(sess: SessionDep, creds: CredModel):
    sess.add(CredsORM(username=creds.username, password=creds.password))
    return {"Регистрация": "успешна"}


@c_router.post("/login", summary="login")
async def login(sess: SessionDep, creds: CredModel):
    query = select(CredsORM)
    res = await sess.execute(query)
    res = res.scalars().all()
    for cred in res:
        if cred.username == creds.username and cred.password == creds.password:
            token = security.create_access_token(uid=str(cred.cred_id))
            response = JSONResponse(content={"Статус": "Авторизация прошла успешно"})
            security.set_access_cookies(token=token, response=response)
            return response
    raise HTTPException(
        status_code=401, detail={"Ошибка авторизации": "Неверные логин или пароль"}
    )


@c_router.get("/users", summary="users")
async def get_users(sess: SessionDep):
    query = select(CredsORM)
    res = await sess.execute(query)
    res = res.scalars().all()
    if res:
        return res
    raise HTTPException(status_code=404, detail={"Ошибка": "Пользователи не найдены"})


@c_router.delete("/del_user", summary="delete user")
async def del_user(sess: SessionDep, username: str):
    query = select(CredsORM).where(CredsORM.username == username)
    user = await sess.execute(query)
    user = user.scalars().first()
    if user:
        await sess.delete(user)
        return {"Статус": "Пользователь удалён"}
    raise HTTPException(status_code=404, detail={"Ошибка": "Пользователь не найден"})


app.include_router(b_router)
app.include_router(c_router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
