import os
import requests
from datetime import datetime
from data_models import db, Author, Book
from flask import Flask, request, render_template, redirect, url_for
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

app = Flask(__name__)

# Get the absolute path to the current directory
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{base_dir}/data/library.sqlite"

db.init_app(app)


# Create the database tables. Run once
# with app.app_context():
   # db.create_all()


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """
    Handles the creation of a new author. The function accepts both GET and POST requests.
    - GET: Renders the form for adding a new author.
    - POST: Processes the form submission, validates the input, and adds the author to the database.
    """
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        birth_date = request.form.get('birth_year', '').strip()
        date_of_death = request.form.get('death_year', '').strip()

        # Validate name: it must contain only alphabetic characters and spaces
        if not name or not name.replace(' ', '').isalpha():
            warning_message = "Author name is required and must contain only letters!"
            return render_template("add_author.html", warning_message=warning_message)

        # Check if the author already exists
        existing_author = Author.query.filter_by(name=name).first()
        if existing_author:
            warning_message = "This author already exists!"
            return render_template("add_author.html", warning_message=warning_message)

        # Validate birth_date and date_of_death
        def validate_date(date_str, field_name):
            if date_str:
                try:
                    return datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    raise ValueError(f"Invalid {field_name}. Please use 'YYYY-MM-DD' format.")
            return None

        try:
            birth_date = validate_date(birth_date, "birth date")
            date_of_death = validate_date(date_of_death, "date of death")

            # Check if date_of_death is after birth_date
            if birth_date and date_of_death and date_of_death <= birth_date:
                warning_message = "Date of death must be after the birth date."
                return render_template("add_author.html", warning_message=warning_message)
        except ValueError as e:
            return render_template("add_author.html", warning_message=str(e))

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
        except SQLAlchemyError:
            db.session.rollback()
            warning_message = f"Error adding author to the database!"
            return render_template("add_author.html", warning_message=warning_message)

    if request.method == "GET":
        return render_template("add_author.html")


def fetch_book_details(isbn):
    """
    Fetches book details, including the cover image URL and description, using the Google Books API.
    Args:
        isbn (str): The ISBN of the book to fetch details for.
    Returns:
        tuple: A tuple containing:
            - cover_url (str or None): The URL of the book's cover image if available, otherwise None.
            - description (str or None): The description of the book if available, otherwise None.
    """
    if not isbn or not isbn.isdigit() or len(isbn) not in (10, 13):
        print(f"Invalid ISBN provided: {isbn}")
        return None, None

    api_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"

    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.Timeout:
        print(f"Request timed out while fetching details for ISBN: {isbn}")
        return None, None
    except requests.exceptions.ConnectionError:
        print(f"Connection error while fetching details for ISBN: {isbn}")
        return None, None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return None, None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching details for ISBN: {isbn}. Error: {e}")
        return None, None

    try:
        data = response.json()
    except ValueError:
        print(f"Error decoding JSON response for ISBN: {isbn}")
        return None, None

    if "items" not in data or not data["items"]:
        print(f"No book found for ISBN: {isbn}")
        return None, None

    try:
        volume_info = data["items"][0]["volumeInfo"]
        cover_url = volume_info.get("imageLinks", {}).get("thumbnail", None)
        description = volume_info.get("description", None)
        return cover_url, description
    except KeyError:
        print(f"Unexpected data structure in API response for ISBN: {isbn}")
        return None, None


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
        isbn = request.form.get('isbn', '').strip()
        title = request.form.get('title', '').strip()
        publication_year = request.form.get('publication_year', '').strip()
        author_id = request.form.get('author_id')
        cover_url = request.form.get('cover_url', '').strip()
        description = request.form.get('description', '').strip()

        # Validate title: it must not be empty and should contain letters
        if not title or not any(char.isalpha() for char in title):
            warning_message = "Book title is required and must contain letters."
            return render_template("add_book.html",
                                   authors=Author.query.all(),
                                   warning_message=warning_message)

        # Validate ISBN: It should contain only digits and be 10 or 13 digits long
        if not isbn.isdigit() or len(isbn) not in [10, 13]:
            warning_message = "Invalid ISBN. It should be 10 or 13 digits."
            return render_template("add_book.html",
                                   authors=Author.query.all(),
                                   warning_message=warning_message)

        # Validate publication year: It should be a valid year
        current_year = datetime.now().year
        if publication_year:
            if not publication_year.isdigit() or not (1000 <= int(publication_year) <= current_year):
                warning_message = f"Invalid publication year. Must be between 1000 and {current_year}."
                return render_template("add_book.html",
                                       authors=Author.query.all(),
                                       warning_message=warning_message)

        # Check if the book already exists
        existing_book = Book.query.filter_by(isbn=isbn).first()
        if existing_book:
            warning_message = "This book already exists in the library!"
            return render_template("add_book.html",
                                   authors=Author.query.all(),
                                   warning_message=warning_message)

        book = Book(
            author_id=author_id,
            isbn=isbn,
            title=title,
            publication_year=int(publication_year) if publication_year else None,
            cover_url=cover_url,
            description=description
        )

        try:
            db.session.add(book)
            db.session.commit()
            success_message = "Book added successfully!"
            return render_template("add_book.html",
                                   authors=Author.query.all(),
                                   success_message=success_message)
        except SQLAlchemyError:
            db.session.rollback()
            warning_message = f"Error adding the book!"
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
            books = db.session.query(Book, Author).join(Author).order_by(Author.name).all()

    books_with_cover = []
    for book, author in books:
        cover_url, _ = fetch_book_details(book.isbn)
        books_with_cover.append((book, author, cover_url))

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
    """
    Displays detailed information about a specific book.
    Args:
        book_id (int): The ID of the book to retrieve details for.
    Returns:
        - Rendered 'book_detail.html' template with:
            - `book`: The book object retrieved from the database.
            - `author`: The author object retrieved from the database.
            - `cover_url`: The book cover URL fetched from the Google Books API.
            - `description`: The book description fetched from the Google Books API.
    """
    book = Book.query.get_or_404(book_id)
    cover_url, description = fetch_book_details(book.isbn)
    author = book.author

    return render_template(
        'book_detail.html',
        book=book,
        author=author,
        cover_url=cover_url,
        description=description
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
