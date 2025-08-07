from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from BooksAPP.main import app
from DataBase.TableModels import CredsORM


class TestBooksApi:

    async def test_all_books(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.get("/books")
            assert response.status_code == 200 and response.json() != {
                "detail": "Books not found"
            }

    async def test_any_book(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            for book_id in range(1, 4):
                response = await ac.get(f"/books/{book_id}")
                assert response.status_code == 200

    async def test_add_book(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            book = {"title": "Forest", "rating": 4.1}
            await ac.post("/books/add_book", json=book)
            get_response = await ac.get(f"/books/4")
            assert (
                get_response.status_code == 200
                and get_response.json()["title"] == book["title"]
            )

    async def test_del_book(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            await ac.delete("/books/remove_book", params={"book_id": 1})
            response = await ac.get("/books")
            books = response.json()
            for book in books:
                assert book["book_id"] != 1 and response.status_code == 200

    async def test_registration(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            creds = {"password": "test1", "username": "test1"}
            await ac.post("/auth/registry", json=creds)
            response = await ac.get("/auth/users")
            assert (
                response.json()[0]["username"] == creds["username"]
                and response.status_code == 200
            )

    async def test_login(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            creds = {"username": "test1", "password": "test1"}
            response = await ac.post("/auth/login", json=creds)
            cookie = response.cookies.get("access_auth")
            assert cookie is not None and response.status_code == 200

    async def test_del_user(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            d_response = await ac.delete("/auth/del_user", params={"username": "test1"})
            g_response = await ac.get("/auth/users")
            users = g_response.json()
            for user in users:
                assert user["username"] != "test1" and d_response.status_code == 200

    async def test_users(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.get("/auth/users")
            assert len(response.json()) == 2 and response.status_code == 200
