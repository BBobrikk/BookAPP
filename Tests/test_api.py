from httpx import AsyncClient, ASGITransport
from BooksAPP.main import app


class TestBooksApi:


    async def test_all_books(self):
        async with AsyncClient(
            transport = ASGITransport(app = app), base_url = "http://test"
        ) as ac:
            response = await ac.get("/books")
            assert response.status_code == 200 and response.json() != {
                "detail": "Books not found"
            }


    async def test_any_book(self):
        async with AsyncClient(
            transport = ASGITransport(app =app), base_url="http://test"
        ) as ac:
            for book_id in range(1, 4):
                response = await ac.get(f"/books/{book_id}")
                assert response.status_code == 200


    async def test_add_book(self):
        async with AsyncClient(
            transport = ASGITransport(app = app), base_url="http://test"
        ) as ac:
            book = {"title": "Forest", "rating": 4.1}
            add_response = await ac.post("/books/add_book", json = book)
            get_response = await ac.get(f"/books/4")
            assert get_response.status_code == 200 and get_response.json()["title"] == book["title"]


    async def test_del_book(self):
        async with AsyncClient(
            transport = ASGITransport(app = app), base_url="http://test"
        ) as ac:
            await ac.delete("/books/remove_book", params={"book_id": 1})
            response = await ac.get("/books")
            books = response.json()
            for book in books:
                assert book["book_id"] != 1
