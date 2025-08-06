from Connection import Base, engine
from Connection import session
from TableModels import BooksORM
import pytest

@pytest.fixture(autouse = True)
async def setup_test_db():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


    async with session() as sess:
        async with sess.begin():
            sess.add_all(
                [
                    BooksORM(title="Little Prince", rating=4.6),
                    BooksORM(title="Game of Thrones", rating=4.4),
                    BooksORM(title="The Walking Dead", rating=4.5),
                ]
            )
            await sess.commit()

    yield

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)