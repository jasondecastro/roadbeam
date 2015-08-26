from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
import random, string

db = SQLAlchemy()

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(100), unique=True)
	firstname = db.Column(db.String(100))
	lastname = db.Column(db.String(100))
	email = db.Column(db.String(120), unique=True)
	pwdhash = db.Column(db.String(54))
	figure = db.Column(db.String(120))
	twitter = db.Column(db.String(120))
	instagram = db.Column(db.String(120))
	github = db.Column(db.String(120))
	location = db.Column(db.String(120))
	bio = db.Column(db.String(120))
	followers = db.Column(db.String(120))
	following = db.Column(db.String(120))
	appreciations = db.Column(db.String(120))

	def __init__(self, firstname, lastname, username, email, password):
		self.firstname = firstname.title()
		self.lastname = lastname.title()
		self.username = username.lower()
		self.email = email.lower()
		self.set_password(password)
		self.figure = "ch-878-1409-72.hd-180-10.sh-3089-64.lg-3202-82-1408.hr-3278-1394-40"
		self.twitter = None
		self.instagram = None
		self.github = None
		self.location = None
		self.bio = None
		self.followers = 0
		self.following = 0
		self.appreciations = 0

	def set_password(self, password):
		self.pwdhash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.pwdhash, password)

class Upload(db.Model):
    __tablename__ = 'upload'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Unicode(255), nullable=False)
    url = db.Column(db.Unicode(255), nullable=False)
    publisher = db.Column(db.Unicode(255), nullable=False)
    title = db.Column(db.Unicode(255), nullable=False)
    description = db.Column(db.Unicode(255), nullable=False)

    def __init__(self, name, url, publisher, title, description):
        self.name = name
        self.url = url
        self.publisher = publisher.lower()
        self.title = title.title()
        self.description = description.title()

