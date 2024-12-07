# Book Alchemy 📚✨

Welcome to **Book Alchemy**, a web application built using Flask that allows users to manage their personal book library. The application provides features to view books, add new books and authors, sort the book collection, and display detailed book information. It integrates with the Google Books API to fetch additional book details like covers and descriptions.

> *This project was developed as part of an assignment in the Software Engineer Bootcamp.* 🎓

## Features 🛠️

- **View Books**: Display a list of books in the library.
- **Sort Books**: Sort books by author or title.
- **Search Books**: Filter books by title for easier searching.
- **Add Books**: Add new books to the library by entering the title, author, ISBN and publication year.
- **Add Authors**: Add authors with their name and birth/death dates.
- **Book Details**: View detailed information about each book, including author, publication year, ISBN, and a description fetched from the Google Books API.
- **Responsive Design**: The app is styled with CSS to ensure a clean and responsive layout across devices.

## Installation ⚙️

```bash
# Clone the repository
git clone https://github.com/Ell-716/Book-Alchemy.git

# Install required dependencies
pip install -r requirements.txt

# Run the Flask application
flask run
```
Visit http://localhost:5000 in your browser to view the app.

## Usage 📖

### Home Page 🏠
- When the app is run, users are directed to the homepage, where they can view a list of books in the library.
- Users can sort the books by author or title and search for books by title.

### Add a New Book 📚✍️
- To add a new book, click the Add a Book button in the header.
- Fill out the form with the book's title, author, ISBN, publication year.

### Add a New Author ✍️
- To add a new author, click the Add an Author button in the header.
- Enter the author's name and birth/death dates.

### Book Details 📃
- To view detailed information about a book, click on the book title.
- The page will display the book's title, author name, and birth/death dates, ISBN, publication year, and a description (if available) fetched from the Google Books API.

## Technologies Used 💻

- **Flask**: Web framework used to create the server-side logic and handle routing.
- **SQLAlchemy**: ORM for managing the database and interacting with book and author data.
- **Jinja2**: Templating engine used to render dynamic content in HTML pages.
- **HTML/CSS**: For designing the user interface.
- **JavaScript**: Used for client-side interactivity, such as dynamic form submissions and sorting without page reloads.
- **Google Books API**: Integrated to fetch additional book details like covers and descriptions.

## Project Requirements 🗂️

- Python 3.x
- Flask 3.0.3
- Flask-SQLAlchemy 3.1.1
- Jinja2 3.1.4
- requests 2.32.3
- SQLAlchemy 2.0.36

## Contributions 🤝

If you'd like to contribute to this project, feel free to submit a pull request. Contributions are welcome in the form of bug fixes, new features, or general improvements. Please ensure that your code is properly tested and follows the style guidelines before submitting.
