from flask_sqlalchemy import SQLAlchemy

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

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

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
        cover_url (str): URL of the book cover image.
        description (str): Description of the book.
    """
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String, nullable=False, unique=True)
    title = db.Column(db.String, nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    cover_url = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)

    author = db.relationship('Author', backref='books', lazy=True)

    def __repr__(self):
        return (f"Book(id = {self.id}, isbn = {self.isbn}, title = {self.title}, "
                f"publication_year = {self.publication_year}, cover_url = {self.cover_url}, "
                f"description = {self.description})")

    def __str__(self):
        """
        Returns a user-friendly string representation of the Book instance.
        """
        return f"{self.id}. {self.title} ({self.publication_year})"
