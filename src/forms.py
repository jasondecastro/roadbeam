from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, PasswordField, SubmitField, validators, ValidationError, BooleanField
from models import db, User

class ContactForm(Form):
  name = TextField("Name",  [validators.Required("Please enter your name.")])
  email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
  subject = TextField("Subject",  [validators.Required("Please enter a subject.")])
  message = TextAreaField("Message",  [validators.Required("Please enter a message.")])
  submit = SubmitField("Send")


class CompleteProfileForm(Form):
  twitter = TextField("Twitter")
  instagram = TextField("Instagram")
  github = TextField("Github")
  location = TextField("Location")
  bio = TextAreaField("Location")
  submit = SubmitField("Sign In")

  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)

class SigninForm(Form):
  username = TextField("Username",  [validators.Required("Please enter your username.")])
  password = PasswordField('Password', [validators.Required("Please enter a password.")])
  remember_me = BooleanField('Remember me')
  submit = SubmitField("Sign In")

  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)

  def validate(self):
    if not Form.validate(self):
      return False

    user = User.query.filter_by(username = self.username.data.lower()).first()
    print user
    if user and user.check_password(self.password.data):
      return True
    else:
      self.username.errors.append("Invalid username or password")
      return False


class SignupForm(Form):
  username = TextField("Username", [validators.Required("Please enter your username.")])
  firstname = TextField("First name",  [validators.Required("Please enter your first name.")])
  lastname = TextField("Last name",  [validators.Required("Please enter your last name.")])
  email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
  password = PasswordField('Password', [validators.Required("Please enter a password.")])
  submit = SubmitField("Create account")

  def __init__(self, *args, **kwargs):
  	Form.__init__(self, *args, **kwargs)

  def validate(self):
    if not Form.validate(self):
      return False

    val_email = User.query.filter_by(email = self.email.data.lower()).first()
    val_user = User.query.filter_by(username = self.username.data.lower()).first()
    print val_user
    print val_email
    if val_email and val_user:
      self.email.errors.append("That email is already taken")
      self.username.errors.append("That username is already taken")
      return False
    elif val_email:
      print 'exists'
      self.email.errors.append("That email is already taken")
      return False
    elif val_user:
      print 'exists'
      self.username.errors.append("That username is already taken")
      return False
    else:
      print 'doesn\'t exist'
      return True