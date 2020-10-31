import os
import secrets
from PIL import Image
from datetime import datetime
from flask import Flask,render_template, url_for, flash, redirect, request, abort
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required,UserMixin,LoginManager
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config['SECRET_KEY'] = '7a92db426dc5bf58777aa19acdaa2044'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Quiz', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    q=db.relationship('Quiz_question', backref='Quiz', lazy=True)

    def __repr__(self):
        return f"Quiz('{self.title}', '{self.date_posted}')"

class Quiz_question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question=db.Column(db.String(100), nullable=False)
    o1=db.Column(db.String(100), nullable=True)
    o2=db.Column(db.String(100), nullable=True)
    o3=db.Column(db.String(100), nullable=True)
    o4=db.Column(db.String(100), nullable=True)
    quiz_no=db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)

    def __repr__(self):
        return f"Quiz_question('{self.question}')" 


posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]

questions = [
  {
    'question': 'What is 2 + 2?',
    'answers': [
      { 'text': '4', 'correct': True },
      { 'text': '22', 'correct': False }
    ]
  },
  {
    'question': 'Who is the best YouTuber?',
    'answers': [
      { 'text': 'Web Dev Simplified', 'correct': True },
      { 'text': 'Traversy Media', 'correct': True },
      { 'text': 'Dev Ed', 'correct': True },
      { 'text': 'Fun Fun Function', 'correct': True }
    ]
  },
  {
    'question': 'Is web development fun?',
    'answers': [
      { 'text': 'Kinda', 'correct': False },
      { 'text': 'YES!!!', 'correct': True },
      { 'text': 'Um no', 'correct': False },
      { 'text': 'IDK', 'correct': False }
    ]
  },
  
]
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)



@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

if __name__ == '__main__':
    app.run(debug=True)