from typing import Annotated
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from DataBase.Connection import session, engine, Base


async def setup_db():
    async with engine.begin() as connect:
        await connect.run_sync(Base.metadata.drop_all)
        await connect.run_sync(Base.metadata.create_all)
        return "Db ready"


async def get_session():
    async with session.begin() as sess:
        yield sess


SessionDep = Annotated[AsyncSession, Depends(get_session)]
