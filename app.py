from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/library.sqlite'

db.init_app(app)