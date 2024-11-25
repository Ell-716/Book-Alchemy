from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Date, ForeignKey

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=True)
    date_of_death = Column(Date, nullable=True)

    def __repr__(self):
        return f"Author(id = {self.id}, name = {self.name})"

    def __str__(self):
        return f"{self.id}. {self.name} ({self.birth_date} - {self.date_of_death})"


class Book(db.Model):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement=True)
    isbn = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    publication_year = Column(Integer, nullable=True)
    author_id = Column(Integer, ForeignKey('authors.id'), nullable=False)

    def __repr__(self):
        return (f"Book(id = {self.id}, isbn = {self.isbn}, title = {self.title}, "
                f"publication_year = {self.publication_year})")

    def __str__(self):
        return f"{self.id}. {self.title} ({self.publication_year})"

