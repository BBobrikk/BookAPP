from sqlalchemy import CheckConstraint
from DataBase.Connection import Base
from sqlalchemy.orm import Mapped, mapped_column


class BooksORM(Base):

    __tablename__ = "Books"

    book_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    rating: Mapped[float]

    def __repr__(self):
        return f"{self.book_id}, {self.title}, {self.rating}"

    __table_args__ = (CheckConstraint("rating between 0 and 5", "CHK_Books_rating"),)


class CredsORM(Base):

    __tablename__ = "Creds"

    cred_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]

    def __repr__(self):
        return f"{self.cred_id}, {self.username}, {self.password}"
