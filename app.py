from flask import Flask, request, render_template
from data_models import db, Author, Book
import os
import requests
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from requests.exceptions import RequestException

app = Flask(__name__)

# Get the absolute path to the current directory
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{base_dir}/data/library.sqlite"

db.init_app(app)

# Create the database tables. Run once
# with app.app_context():
#     db.create_all()


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        name = request.form.get('name').strip()
        birth_date = request.form.get('birth_date')
        date_of_death = request.form.get('date_of_death')

        if not name:  # Ensure the name is not empty
            warning_message = "Author name is required."
            return render_template("add_author.html", warning_message=warning_message)

        # Validate birth date and date of death
        try:
            if birth_date and not datetime.strptime(birth_date, "%Y-%m-%d"):
                raise ValueError("Birth date must be in YYYY-MM-DD format.")
        except ValueError as e:
            warning_message = f"Invalid birth date: {e}"
            return render_template("add_author.html", warning_message=warning_message)

        try:
            if date_of_death and not datetime.strptime(date_of_death, "%Y-%m-%d"):
                raise ValueError("Date of death must be in YYYY-MM-DD format.")
        except ValueError as e:
            warning_message = f"Invalid date of death: {e}"
            return render_template("add_author.html", warning_message=warning_message)

        author = Author(
            name=name,
            birth_date=birth_date if birth_date else None,
            date_of_death=date_of_death if date_of_death else None
        )

        try:
            db.session.add(author)
            db.session.commit()
            success_message = "Author added successfully!"
            return render_template("add_author.html", success_message=success_message)
        except SQLAlchemyError as e:
            db.session.rollback()
            warning_message = f"Error adding author to the database: {e}"
            return render_template("add_author.html", warning_message=warning_message)

    if request.method == "GET":
        return render_template("add_author.html")


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        isbn = request.form.get('isbn').strip()
        title = request.form.get('title').strip()
        publication_year = request.form.get('publication_year').strip()
        author_id = request.form.get('author_id')

        if not title:
            warning_message = "Book title is required."
            return render_template("add_book.html",
                                   authors=Author.query.all(),
                                   warning_message=warning_message)

        # Validate ISBN
        if not isbn.isdigit() or len(isbn) not in [10, 13]:
            warning_message = "Invalid ISBN. It should be 10 or 13 digits."
            return render_template("add_book.html",
                                   authors=Author.query.all(),
                                   warning_message=warning_message)

        book = Book(
            author_id=author_id,
            isbn=isbn,
            title=title,
            publication_year=publication_year if publication_year else None
        )

        try:
            db.session.add(book)
            db.session.commit()
            success_message = "Book added successfully!"
            return render_template("add_book.html",
                                   authors=Author.query.all(),
                                   success_message=success_message)
        except SQLAlchemyError as e:
            db.session.rollback()
            warning_message = f"Error adding book to the database: {e}"
            return render_template("add_book.html",
                                   authors=Author.query.all(),
                                   warning_message=warning_message)

    if request.method == "GET":
        return render_template("add_book.html", authors=Author.query.all())


@app.route("/", methods=["GET"])
def home_page():
    # Default sorting and search criteria
    sort = request.args.get('sort', 'author')
    search = request.args.get('search', '').strip()

    books_with_cover = []

    # Handle search query
    if search:
        books = db.session.query(Book, Author).join(Author).filter(Book.title.like(f"%{search}%")).all()
        if not books:
            message = f"No books found matching '{search}'."
            return render_template("home.html", books=[], sort=sort, message=message)

    # Handle sorting query
    else:
        if sort == 'author':
            books = db.session.query(Book, Author).join(Author).order_by(Author.name).all()
        elif sort == 'title':
            books = db.session.query(Book, Author).join(Author).order_by(Book.title).all()
        else:
            books = db.session.query(Book, Author).join(Author).all()

    # Fetch book cover images
    for book, author in books:
        isbn = book.isbn
        google_books_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"

        try:
            response = requests.get(google_books_url)
            cover = None
            if response.status_code == 200:
                data = response.json()
                if "items" in data:
                    cover = data["items"][0].get("volumeInfo", {}).get("imageLinks", {}).get("thumbnail", None)

            books_with_cover.append((book, author, cover))
        except RequestException as e:
            print(f"Error fetching cover for ISBN {isbn}: {e}")
            books_with_cover.append((book, author, None))

    return render_template("home.html", books=books_with_cover, sort=sort, search=search)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
