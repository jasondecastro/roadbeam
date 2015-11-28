from src import app
from flask import url_for, redirect, session, render_template, request, flash, jsonify
from forms import SignupForm, SigninForm, CompleteProfileForm
from models import db, User, Upload, Follow, Posts
import os, os.path, random, requests, string, threading, shutil, urllib
from flask import Flask, redirect, request, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func, select
from werkzeug import secure_filename


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    upload_folder = '/Users/developeraccount/Desktop/Roadbeam/roadbeam/src/static/accounts/%s' % session['username']
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

def quality_check(post):
  return True

@app.route('/getTextPost', methods=['GET', 'POST'])
def getTextPost():
  user_post = str(request.form["text_post"])
  user = User.query.filter_by(username = session['username']).first()
  
  if len(user_post) < 340:
    if quality_check(user_post):
      new_post = Posts(user.firstname, user.lastname, user.username, user.id, user_post, None, None)
      db.session.add(new_post)
      db.session.commit()
      return jsonify({'success': 'true'})
    else:
      return 'no quality'
  else:
    return 'too large'

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
    return render_template('gallery.html', username=username, uploads=uploads)

@app.route('/')
def home():
  return render_template('index.html')

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

@app.route('/follow/<username>', methods=['GET', 'POST'])
def follow(username):
  if 'username' not in session:
    return redirect(url_for('signin'))

  follower = User.query.filter_by(username=session['username']).first()
  
  try:
    followed = User.query.filter_by(username=username).first()
  except:
    return 'no such user exists ===('

  if Follow.query.filter((Follow.follower_username==session['username']) & (Follow.followed_username==username)).count() >= 1:
    return 'you can\'t follow the same guy twice dude..'
  else:
    add_follower = Follow(username, session['username'], followed.id, follower.id)
    db.session.add(add_follower)
    db.session.commit()
  return jsonify({'success': 'true'})

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
  if 'username' not in session:
    return redirect(url_for('signin'))

  user = User.query.filter_by(username = session['username']).first()
  uploads = Upload.query.filter_by(publisher=session['username'])

  following = Follow.query.filter_by(follower_username=session['username'])
  following_count = []
  for i in following:
    following_count.append(i)
  amount_of_following = len(following_count)
  user.following = amount_of_following
  db.session.commit()

  followers_count = []
  for person in User.query.all():
    followers = Follow.query.filter_by(followed_username=person.username)

    if followers != None:
      for i in followers:
        followers_count.append(i)

        amount_of_followers = len(followers_count)
        User.query.filter_by(username=person.username).first().followers = amount_of_followers
        db.session.commit()
    else:
      amount_of_followers = 0
      User.query.filter_by(username=person.username).first().followers = amount_of_followers
      db.session.commit()

  random_people = []

  for i in User.query.order_by(func.rand()).limit(2).all():
    random_people.append(i)

  #work on filtering posts

  peopleFollowing = []
  for i in Follow.query.filter_by(follower_username=session['username']):
    peopleFollowing.append(i.followed_username)


  posts_query = Posts.query.all()
  postsFollowing = [session['username']]

  for i in posts_query:
    if i.poster_username in peopleFollowing:
      postsFollowing.append(i.poster_username)

  posts = Posts.query.filter(Posts.poster_username.in_(postsFollowing))

  upload_folder = '/Users/developeraccount/Desktop/Roadbeam/roadbeam/src/static/accounts/%s' % session['username']

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


    return render_template('dashboard.html', User=User, peopleFollowing=peopleFollowing, posts=posts, random_people=random_people, bio=bio, uploads=uploads, location=location,
                            github=github, instagram=instagram, username=username, firstname=firstname,
                            lastname=lastname, figure=figure, following=following,
                            followers=followers, twitter=twitter,
                            appreciations=appreciations)

@app.route('/getFollowers', methods=['GET', 'POST'])
def getFollowers():
  user = User.query.filter_by(username=session['username']).first()

  randomPeople = []
  theUserDatabase = User.query.all()
  listOfUsernames = []
  theFollowersDatabase = Follow.query.all()
  listOfFollowers = {}
  for everyUser in theUserDatabase:
    listOfUsernames.append(everyUser.username)
  for everyFollower in theFollowersDatabase:
    listOfFollowers[everyFollower.followed_username] = everyFollower.follower_username

  print listOfUsernames
  print listOfFollowers

  peopleFollowedAlready = []
  peopleHaventFollowedAlready = listOfUsernames

  if set(listOfUsernames) & set(listOfFollowers):
    print 'yes'
    randomPerson = random.choice(listOfUsernames)
    for key in listOfFollowers:
      print 'good'
      if session['username'] == listOfFollowers[key]:
        print 'test'
        peopleFollowedAlready.append(key)
        peopleHaventFollowedAlready.remove(key)
      else:
        print 'nope'

  try:
    personToRemove = random.choice(peopleHaventFollowedAlready)
  except IndexError:
    print 'You have followed everyone.'

  if personToRemove in peopleFollowedAlready:
    peopleHaventFollowedAlready.remove(personToRemove)
  print 'yes'
  print peopleHaventFollowedAlready
  print peopleFollowedAlready

  returnedFollower = User.query.filter_by(username=personToRemove).first()
  return jsonify({'success': [returnedFollower.firstname, returnedFollower.lastname, returnedFollower.username] })  

@app.route('/unfollow/<followed_username>', methods=['GET', 'POST'])
def unfollowUser(followed_username):
  print 'this is good 1'
  print 'this is good 2'
  user = Follow.query.filter_by(followed_username=followed_username)
  print 'this is good 3'
  for personFollowing in user:
    if Follow.query.filter((Follow.followed_username==followed_username) & (Follow.follower_username==session['username'])).count() >= 1:
      # db.session.delete(Follow.query.filter((Follow.followed_username==followed_username) & (Follow.follower_username==session['username'])))
      db.session.delete(user)
      db.session.commit()

  return jsonify({'success': 'you have unfollowed this user'})

  # if User.query.filter_by(username=username).first().followers >= 1:
  #   a = Follow.query.filter_by(followed_username=username)
  #   for i in a:
  #     if user.username != a.follower_username:
  #       print a.follower_username
  #       print 'you is not following person'

  # # followers = []
  # # for i in User.query.all():
  # #   print i.followers
  # #   if i.followers >= 1:
  # #     print i.followers
  # #     print i.username
  # #     a = Follow.query.filter_by(followed_username=i).first()
  # #     print a
  # #     if user.username != a.follower_username:
  # #       followers.append(i)
  # #   else:
  # #     followers.append(i)

# def randomword(length):
#   return u''.join(random.choice(string.lowercase) for i in range(length))

# def profileSetup(username, db):
#   topics = ["abstract", "animals", "business", "cats", "city", "food", "nightlife", "fashion", "people", "nature", "sports", "technics", "transport"]

#   count = 0
#   while count <= 15:
#     url = "http://lorempixel.com/1900/1200/%s/" % random.choice(topics)
#     response = requests.get(url)
#     if response.status_code == 200:
#       print url
#       filename = randomword(7) + ".jpg"
#       f = open("/Users/developeraccount/Desktop/Roadbeam/roadbeam/src/static/accounts/%s/%s" % (username, filename), 'wb')
#       f.write(response.content)
#       f.close()

#       with app.app_context():
#         newupload = Upload(filename, 'accounts/%s/%s' % (username, filename), username, "none", "none")
#         db.session.add(newupload)
#         db.session.commit()

#     count = count + 1

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
      newuser = User(form.firstname.data, form.lastname.data, form.username.data, form.password.data)
      # add_follower = Follow(username, session['username'], followed.id, follower.id)
      db.session.add(newuser)
      # db.session.add(add_follower)
      db.session.commit()

      session['username'] = newuser.username

      if not os.path.exists("/Users/developeraccount/Desktop/Roadbeam/roadbeam/src/static/accounts/%s" % session['username']):
        os.mkdir("/Users/developeraccount/Desktop/Roadbeam/roadbeam/src/static/accounts/%s" % session['username'])
      
      if not os.path.exists("/Users/developeraccount/Desktop/Roadbeam/roadbeam/src/static/accounts/%s/profile_picture" % session['username']):
        os.mkdir("/Users/developeraccount/Desktop/Roadbeam/roadbeam/src/static/accounts/%s/profile_picture" % session['username'])

      if not os.path.exists("/Users/developeraccount/Desktop/Roadbeam/roadbeam/src/static/accounts/%s/cover_picture" % session['username']):
        os.mkdir("/Users/developeraccount/Desktop/Roadbeam/roadbeam/src/static/accounts/%s/cover_picture" % session['username'])

      url = 'http://invatar0.appspot.com/svg/%s%s.jpg?s=256' % (form.firstname.data[:1], form.lastname.data[:1])
      # response = requests.get(url)
      # print response.content
      # with open('/Users/developeraccount/Desktop/Roadbeam/roadbeam/src/static/accounts/%s/profile_picture/profile.jpg' % session['username'], 'wb') as out_file:
      #     out_file.write(response.content)
      # del response

      # urllib.urlretrieve(url, '/Users/developeraccount/Desktop/Roadbeam/roadbeam/src/static/accounts/%s/profile_picture/profile.jpg' % session['username'])

      response = requests.get(url)
      if response.status_code == 200:
        f = open('/Users/developeraccount/Desktop/Roadbeam/roadbeam/src/static/accounts/%s/profile_picture/profile.jpg' % session['username'], 'wb')
        f.write(response.content)
        f.close()

      session['completeprofile'] = newuser.username

      # threading.Thread(target=profileSetup, args=(session['username'], db)).start()

      return redirect(url_for('verify'))

      # return redirect(url_for('somedetails')) # do this if verify email sucks

  elif request.method == 'GET':
    return render_template('signup.html', form=form)

@app.route('/verify', methods=['GET', 'POST'])
def verify():
  return render_template('verifyemail.html')

@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
  # user_table = User.query.filter_by(username = session['username']).first()
  # for user in user_table:
  #   print user 
  return render_template('confirmcode.html')

def send_email(user, pwd, recipient, subject, body):
  import smtplib
  print body

  gmail_user = user
  gmail_pwd = pwd
  FROM = user
  TO = recipient if type(recipient) is list else [recipient]
  SUBJECT = subject
  TEXT = body

  message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
  """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
  # try:
  server = smtplib.SMTP("smtp.gmail.com", 587)
  server.starttls()
  server.login(gmail_user, gmail_pwd)
  server.sendmail(FROM, TO, message)
  server.quit()
  print 'successfully sent the mail'
  # except:
  #     print "failed to send mail"

@app.route('/sendVerificationCode', methods=['GET', 'POST'])
def sendVerificationCode():
  email_to_send_code_to = request.form['email_to_send_code_to']
  user = User.query.filter_by(username = session['username']).first()

  send_email("roadbeam.noreply@gmail.com", "roadbeam.com", email_to_send_code_to, "Your Verification Code", user.verification_code)
  
  return jsonify({"email_to_send_code_to": email_to_send_code_to}) #security flaw

@app.route('/getVerificationCode', methods=['GET', 'POST'])
def getVerificationCode():
  code = request.form["code"]
  user = User.query.filter_by(username = session['username']).first()

  if code == user.verification_code:
    return jsonify({'success': 'true'})
  else:
    return jsonify({'success': 'false'})


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
