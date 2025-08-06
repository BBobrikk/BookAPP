from pydantic import BaseModel
from Parameters import host, port, user, password, db_name


class Settings(BaseModel):
    port: str
    host: str
    user: str
    password: str
    db_name: str

    # def SYNC_ENGINE_CREATE(self):
    #     return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"

    def ASYNC_ENGINE_CREATE(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"


settings = Settings(port=port, host=host, user=user, password=password, db_name=db_name)
