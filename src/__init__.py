from flask import Flask

 
app = Flask(__name__)

import random
app.jinja_env.globals.update(randint=random.randint)
 
app.secret_key = 'development key'
 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/development'
 
from models import db
db.init_app(app)

import src.routes

