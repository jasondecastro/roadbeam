from src import app
from flask import url_for, redirect, session, render_template, request, flash
from forms import SignupForm, SigninForm, CompleteProfileForm
from models import db, User, Upload
import os, os.path, random, requests, string, threading
from flask import Flask, redirect, request, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import secure_filename

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    upload_folder = '/Users/Bryans-MacBook-Pro/Desktop/Development/Roadbeam/src/static/accounts/%s' % session['username']
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename.lower()):
            filename = secure_filename(file.filename)
            newupload = Upload(filename, 'accounts/%s/%s' % (session['username'], filename), session['username'], request.form['title'], request.form['description'])
            db.session.add(newupload)
            db.session.commit()
            file.save(os.path.join(upload_folder, filename))
            return redirect(url_for('upload'))
    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
          <input type="text" name="title" placeholder="title">
          <input type="text" name="description" placeholder="description">
         <input type=submit value=Upload>
    </form>
    <p>%s</p>
    """ % "<br>".join(os.listdir(upload_folder,))

@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def remove(id):
    """Delete an uploaded file."""
    upload = Upload.query.get_or_404(id)

    if upload.publisher == session['username']:
        db.session.delete(upload)
        db.session.commit()
    else:
      return 'you do not have right perms'

    return redirect(url_for('dashboard'))

@app.route("/<username>/gallery")
def gallery(username):
    uploads = Upload.query.all()
    return (
        '<a href="/upload">New Upload</a><br>' +
        u''.join(
            u'<a href="/static/accounts/%s/%s">%s</a>'
            u'<form action="/delete/%s" method="POST">'
            u'  <button type="submit">Delete</button>'
            u'</form><br>'
            % (u.publisher, u.name, u.name, u.id)
            for u in uploads if u.publisher == username
        )
    )


@app.route('/')
def home():
  return redirect(url_for('signin'))

@app.route('/account/settings', methods=['GET', 'POST'])
def accountsettings():
  form = CompleteProfileForm()

  user = User.query.filter_by(username = session['username']).first()

  if request.method == 'POST':
    if form.validate() == False:
      return render_template('accountsettings.html', form=form)
    else:
      if form.twitter.data >= 1:
        user.twitter = form.twitter.data
        db.session.commit()
      if form.instagram.data >= 1:
        user.instagram = form.instagram.data
        db.session.commit()
      if form.github.data >= 1:
        user.github = form.github.data
        db.session.commit()
      if form.location.data >= 1:
        user.location = form.location.data
        db.session.commit()
      if form.bio.data >= 1:
        user.bio = form.bio.data
        db.session.commit()

      return redirect(url_for('accountdetails'))

  elif request.method == 'GET':
    if user is None:
      print 'yes'
      return redirect(url_for('signin'))
    else:
      firstname = user.firstname
      lastname = user.lastname
      username = user.username
      figure = user.figure
      location = user.location
      following = user.following
      followers = user.followers
      twitter = user.twitter
      appreciations = user.appreciations
      instagram = user.instagram
      github = user.github
      bio = user.bio
      location = user.location



      return render_template('accountsettings.html', form=form, bio=bio, location=location,
                              github=github, instagram=instagram, username=username, firstname=firstname,
                              lastname=lastname, figure=figure, following=following,
                              followers=followers, twitter=twitter,
                              appreciations=appreciations)

@app.route('/account/details')
def accountdetails():
  form = CompleteProfileForm()

  if 'username' not in session:
    return redirect(url_for('signin'))

  user = User.query.filter_by(username = session['username']).first()

  if user is None:
    return redirect(url_for('signin'))
  else:
    firstname = user.firstname
    lastname = user.lastname
    username = user.username
    figure = user.figure
    location = user.location
    following = user.following
    followers = user.followers
    twitter = user.twitter
    appreciations = user.appreciations
    instagram = user.instagram
    github = user.github
    bio = user.bio
    location = user.location


    return render_template('accountdetails.html', form=form, bio=bio, location=location,
                            github=github, instagram=instagram, username=username, firstname=firstname,
                            lastname=lastname, figure=figure, following=following,
                            followers=followers, twitter=twitter,
                            appreciations=appreciations)

@app.route('/somedetails', methods=['GET', 'POST'])
def somedetails():
  form = CompleteProfileForm()

  if 'completeprofile' not in session:
    return redirect(url_for('dashboard'))

  if request.method == 'POST':
    if form.validate() == False:
      return render_template('somedetails.html', form=form)
    else:
      userinfo = User.query.filter_by(username=session['username']).first()
      if form.twitter.data >= 1:
        userinfo.twitter = form.twitter.data
        db.session.commit()
      if form.instagram.data >= 1:
        userinfo.instagram = form.instagram.data
        db.session.commit()
      if form.github.data >= 1:
        userinfo.github = form.github.data
        db.session.commit()
      if form.location.data >= 1:
        userinfo.location = form.location.data
        db.session.commit()
      if form.bio.data >= 1:
        userinfo.bio = form.bio.data
        db.session.commit()

      session.pop('completeprofile', None)

      return redirect(url_for('dashboard'))

  elif request.method == 'GET':
    return render_template('somedetails.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
  if 'username' not in session:
    return redirect(url_for('signin'))

  user = User.query.filter_by(username = session['username']).first()
  upload_folder = '/Users/Bryans-MacBook-Pro/Desktop/Development/Roadbeam/src/static/accounts/%s' % session['username']

  if user is None:
    return redirect(url_for('signin'))
  else:
    firstname = user.firstname
    lastname = user.lastname
    username = user.username
    figure = user.figure
    location = user.location
    following = user.following
    followers = user.followers
    twitter = user.twitter
    appreciations = user.appreciations
    instagram = user.instagram
    github = user.github
    bio = user.bio
    location = user.location

    if request.method == 'POST':
      file = request.files['file']
      if file and allowed_file(file.filename.lower()):
          filename = secure_filename(file.filename)
          # newupload = Upload(filename, '/accounts/%s/%s' % (session['username'], filename), session['username'], request.form['title'], request.form['description'])
          newupload = Upload(filename, 'accounts/%s/%s' % (session['username'], filename), session['username'], "none", "none")
          db.session.add(newupload)
          db.session.commit()
          file.save(os.path.join(upload_folder, filename))
          return redirect(url_for('dashboard'))


    return render_template('dashboard.html', bio=bio, location=location,
                            github=github, instagram=instagram, username=username, firstname=firstname,
                            lastname=lastname, figure=figure, following=following,
                            followers=followers, twitter=twitter,
                            appreciations=appreciations)

def randomword(length):
  return u''.join(random.choice(string.lowercase) for i in range(length))

def profileSetup(username, db):
  topics = ["abstract", "animals", "business", "cats", "city", "food", "nightlife", "fashion", "people", "nature", "sports", "technics", "transport"]

  count = 0
  while count <= 15:
    url = "http://lorempixel.com/1900/1200/%s/" % random.choice(topics)
    response = requests.get(url)
    if response.status_code == 200:
      print url
      filename = randomword(7) + ".jpg"
      f = open("/Users/Bryan/Desktop/Development/roadbeam/src/static/accounts/%s/%s" % (username, filename), 'wb')
      f.write(response.content)
      f.close()

      with app.app_context():
        newupload = Upload(filename, 'accounts/%s/%s' % (username, filename), username, "none", "none")
        db.session.add(newupload)
        db.session.commit()

    count = count + 1

#-- REGISTER PAGE --#
@app.route('/signup', methods=['GET', 'POST'])
def signup():
  form = SignupForm()

  if 'username' in session:
    return redirect(url_for('somedetails'))

  if request.method == 'POST':
    if form.validate() == False:
      return render_template('signup.html', form=form)
    else:
      newuser = User(form.firstname.data, form.lastname.data, form.username.data, form.email.data, form.password.data)
      db.session.add(newuser)
      db.session.commit()

      session['username'] = newuser.username

      if not os.path.exists("/Users/Bryan/Desktop/Development/roadbeam/src/static/accounts/%s" % session['username']):
        os.mkdir("/Users/Bryan/Desktop/Development/roadbeam/src/static/accounts/%s" % session['username'])

      session['completeprofile'] = newuser.username

      threading.Thread(target=profileSetup, args=(session['username'], db)).start()

      return redirect(url_for('somedetails'))

  elif request.method == 'GET':
    return render_template('signup.html', form=form)


#-- LOGIN PAGE --#
@app.route('/signin', methods=['GET', 'POST'])
def signin():
  form = SigninForm()

  if 'username' in session:
    return redirect(url_for('dashboard'))

  if request.method == 'POST':
    if form.validate() == False:
      return render_template('signin.html', form=form)
    else:
      session['username'] = form.username.data
      return redirect(url_for('dashboard'))

  elif request.method == 'GET':
    return render_template('signin.html', form=form)


#-- LOGOUT PAGE --#
@app.route('/signout')
def signout():

  if 'username' not in session:
    return redirect(url_for('signin'))

  session.pop('username', None)
  return redirect(url_for('home'))

#-- PROFILE PAGE --#
@app.route('/<username>')
def profile(username):
  # if 'username' not in session:
  #   return redirect(url_for('signin'))
  user = User.query.filter_by(username = username).first()
  uploads = Upload.query.filter_by(publisher=username)

  if user is None:
    return render_template('404.html')
  else:
    firstname = user.firstname
    lastname = user.lastname
    username = user.username
    figure = user.figure
    location = user.location
    following = user.following
    followers = user.followers
    twitter = user.twitter
    appreciations = user.appreciations
    instagram = user.instagram
    github = user.github
    bio = user.bio
    location = user.location
    if 'username' in session:
        profile_owner = session['username']
    else:
        profile_owner = None



    return render_template('profile.html', uploads=uploads, bio=bio, location=location,
                            github=github, instagram=instagram, username=username, firstname=firstname,
                            lastname=lastname, figure=figure, following=following,
                            followers=followers, twitter=twitter, profile_owner=profile_owner,
                            appreciations=appreciations)
