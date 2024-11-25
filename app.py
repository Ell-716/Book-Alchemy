from flask import Flask, request, render_template
from data_models import db, Author, Book
import os
import requests

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

        author = Author(
            name=name,
            birth_date=birth_date if birth_date else None,
            date_of_death=date_of_death if date_of_death else None
        )

        db.session.add(author)
        db.session.commit()

        success_message = "Author added successfully!"
        return render_template("add_author.html", success_message=success_message)

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

        book = Book(
            author_id=author_id,
            isbn=isbn,
            title=title,
            publication_year=publication_year if publication_year else None
        )

        db.session.add(book)
        db.session.commit()

        success_message = "Book added successfully!"
        return render_template("add_book.html",
                               authors=Author.query.all(),
                               success_message=success_message)

    if request.method == "GET":
        return render_template("add_book.html", authors=Author.query.all())


@app.route("/", methods=["GET"])
def home_page():
    # Query all books and join with the author table to get author names
    books = db.session.query(Book, Author).join(Author).all()

    # Fetch book cover images using Google Books API
    for i, (book, author) in enumerate(books):
        isbn = book.isbn
        google_books_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"

        response = requests.get(google_books_url)

        if response.status_code == 200:
            data = response.json()
            if "items" in data:
                book_cover = data["items"][0].get("volumeInfo", {}).get("imageLinks", {}).get("thumbnail", None)
                books[i] = (book, author, book_cover)
            else:
                books[i] = (book, author, None)
        else:
            books[i] = (book, author, None)

    return render_template("home.html", books=books)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)