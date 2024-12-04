import os
import requests
from datetime import datetime
from data_models import db, Author, Book
from flask import Flask, request, render_template, redirect, url_for
from requests.exceptions import RequestException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

app = Flask(__name__)

# Get the absolute path to the current directory
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{base_dir}/data/library.sqlite"

db.init_app(app)


# Create the database tables. Run once
# with app.app_context():
#     db.create_all()


@app.route("/add_author", methods=["GET", "POST"])
@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """
    Handles the creation of a new author. The function accepts both GET and POST requests.
    - GET: Renders the form for adding a new author.
    - POST: Processes the form submission, validates the input, and adds the author to the database.
    """
    if request.method == "POST":
        name = request.form.get('name').strip()
        birth_date = request.form.get('birth_year')
        date_of_death = request.form.get('death_year')

        if not name:  # Ensure the name is not empty
            warning_message = "Author name is required."
            return render_template("add_author.html", warning_message=warning_message)

        # Convert birth_date and date_of_death to datetime objects if provided
        if birth_date:
            try:
                birth_date = datetime.strptime(birth_date, "%Y-%m-%d")  # Ensure correct date format
            except ValueError:
                birth_date = None  # Handle incorrect date format
        else:
            birth_date = None

        if date_of_death:
            try:
                date_of_death = datetime.strptime(date_of_death, "%Y-%m-%d")  # Ensure correct date format
            except ValueError:
                date_of_death = None  # Handle incorrect date format
        else:
            date_of_death = None

        # Create the Author object
        author = Author(
            name=name,
            birth_date=birth_date,
            date_of_death=date_of_death
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
    """
    Handles the creation of a new book. The function accepts both GET and POST requests.
    - GET: Renders the form for adding a new book.
    - POST: Processes the form submission, validates the input, and adds the book to the database.

    Returns:
        - Rendered HTML templates based on the success or failure of adding the book.
    """
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
    """
    Displays the homepage with a list of books. The books can be sorted by author or title,
    and a search functionality is available to filter books by title.

    Returns:
        - Rendered homepage with books, sorted and/or filtered based on the user's input.
    """
    sort = request.args.get('sort', 'author')
    search = request.args.get('search') or ""
    message = request.args.get('message')

    if search:
        books = db.session.query(Book, Author).join(Author) \
            .filter(Book.title.like(f"%{search}%")) \
            .order_by(Book.title).all()
        if not books:
            return render_template("home.html", books=[], search=search,
                                   message="No books found matching your search.")
    else:
        if sort == 'author':
            books = db.session.query(Book, Author).join(Author).order_by(Author.name).all()
        elif sort == 'title':
            books = db.session.query(Book, Author).join(Author).order_by(Book.title).all()
        else:
            # Default sorting by author if the sort parameter is not valid or missing
            books = db.session.query(Book, Author).join(Author).order_by(Author.name).all()

    # Fetch book covers and combine data
    books_with_cover = []
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
        except RequestException:
            books_with_cover.append((book, author, None))

    return render_template("home.html", books=books_with_cover,
                           sort=sort, search=search, message=message)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    """
    Deletes a book from the database and removes the author if they no longer have any books.

    Args:
        book_id (int): The ID of the book to be deleted.

    Returns:
        - Redirects to the homepage with a success or error message.
    """
    try:
        book_to_delete = db.session.query(Book).filter(Book.id == book_id).first()
        if not book_to_delete:
            return redirect(url_for('home_page', message=f"Book with ID {book_id} not found!"))

        book_title = book_to_delete.title
        author_id = book_to_delete.author_id

        db.session.query(Book).filter(Book.id == book_id).delete()

        # Check if the author has other books, and delete the author if none exist
        if not db.session.query(Book).filter(Book.author_id == author_id).count():
            db.session.query(Author).filter(Author.id == author_id).delete()

        db.session.commit()
        return redirect(url_for('home_page', message=f"Book '{book_title}' deleted successfully!"))

    except IntegrityError as e:
        db.session.rollback()
        print(f"IntegrityError: {e}")
        return redirect(url_for('home_page', message="Database integrity error occurred during deletion."))
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"SQLAlchemyError: {e}")
        return redirect(url_for('home_page', message="An unexpected error occurred. Please try again."))


@app.route('/book/<int:book_id>')
def book_detail(book_id):
    # Retrieve the book from your database
    book = Book.query.get_or_404(book_id)

    # Fetch additional data from Google Books API
    google_books_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{book.isbn}"
    response = requests.get(google_books_url)
    google_data = response.json()

    # Extract book information from Google Books API response
    book_info = google_data.get('items', [{}])[0].get('volumeInfo', {})

    # Get author information (assuming it's linked to the book)
    author = book.author

    return render_template('book_detail.html', book=book, author=author, book_info=book_info)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
