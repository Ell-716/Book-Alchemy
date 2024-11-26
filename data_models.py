from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey

db = SQLAlchemy()


class Author(db.Model):
    """
    Author model representing an author in the database.

    Attributes:
        id (int): Primary key for the author.
        name (str): Name of the author.
        birth_date (str): Birth date of the author in 'YYYY-MM-DD' format.
        date_of_death (str): Date of death of the author in 'YYYY-MM-DD' format.
    """
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    birth_date = Column(String, nullable=True)
    date_of_death = Column(String, nullable=True)

    def __repr__(self):
        """
        Returns a string representation of the Author instance for debugging.
        """
        return f"Author(id = {self.id}, name = {self.name})"

    def __str__(self):
        """
        Returns a user-friendly string representation of the Author instance.
        """
        return f"{self.id}. {self.name} ({self.birth_date} - {self.date_of_death})"


class Book(db.Model):
    """
    Book model representing a book in the database.

    Attributes:
        id (int): Primary key for the book.
        isbn (str): ISBN of the book, should be unique.
        title (str): Title of the book.
        publication_year (int): Year the book was published.
        author_id (int): Foreign key referencing the Author of the book.
    """
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement=True)
    isbn = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    publication_year = Column(Integer, nullable=True)
    author_id = Column(Integer, ForeignKey('authors.id'), nullable=False)

    def __repr__(self):
        """
        Returns a string representation of the Book instance for debugging.
        """
        return (f"Book(id = {self.id}, isbn = {self.isbn}, title = {self.title}, "
                f"publication_year = {self.publication_year})")

    def __str__(self):
        """
        Returns a user-friendly string representation of the Book instance.
        """
        return f"{self.id}. {self.title} ({self.publication_year})"
