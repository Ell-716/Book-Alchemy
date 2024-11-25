from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book
import os

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
        birth_date = request.form.get('birth_date').strip()
        date_of_death = request.form.get('date_of_death').strip()

        if not name:  # Ensure the name is not empty
            success_message = "Author name is required."
            return redirect(url_for('add_author', success_message=success_message))

        author = Author(
            name=name,
            birth_date=birth_date if birth_date else None,
            date_of_death=date_of_death if date_of_death else None
        )

        db.session.add(author)
        db.session.commit()

        success_message = "Author added successfully!"

        # Redirect to the same page with success message in the URL
        return redirect(url_for('add_author', success_message=success_message))

    if request.method == "GET":
        return render_template("add_author.html")
