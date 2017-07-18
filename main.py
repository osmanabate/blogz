#__author__: "osman abate"
#__version__: "1.0"
# date: 07/08/2017
# assignment: Blogz
# collaborated with "Abdulkarim Abate"
from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:lc101@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'welloethio'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, content):
        self.title = title
        self.content = content
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    posts = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email']=email

            return redirect('/')
        else:

            return '<h1>Invalid input, please try again!</h1>'

    return render_template('login.html')

@app.before_request
def require_login():
    allowd_routes =['login', 'signup']
    if request.endpoint not in allowd_routes and 'email' not in session:
        return redirect('/login')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        email_error = ''
        existing_email_error = ''
        verify_error = ''

        if len(email)>=120 or len(email)==0:
            email_error = "Please enter a valid email"
            return email_error

        if len(email_error)>0:
            return "Tast"

        if password != verify:
            verify_error = "password does not match, please try again"
            return verify_error


        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email']=email

            return redirect('/')
        else:
            existing_email_error = "email already in use"

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

@app.route('/', methods=['POST', 'GET'])
def index():

    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        error_title = ""
        error_content =""
        blog_title = request.form['title']
        blog_content = request.form['content']
        if len(blog_title) >=120 or len(blog_title) ==0:
            error_title = "Your title length exceeds the limit, please shorten your title."
            blog_title =""
        if len(blog_content) >=1000 or len(blog_content) ==0:
            error_content = "your content length exceeds the limit, please shorten your content."
            blog_content = ""
        if len(error_title)>0 or len(error_content)>0:
            return render_template('index.html', title= blog_title, content= blog_content, error_title=error_title, error_content=error_content)
        else:
            new_blog = Blog(blog_title, blog_content)
            db.session.add(new_blog)
            db.session.commit()
            return redirect("/blog_page?id=" +str(new_blog.id))

    else:
        posts = Blog.query.all()

    posts = Blog.query.filter_by(owner=owner).all()
    return render_template('index.html', page_name= 'Add a blog Entry', posts= posts)

@app.route('/blog_page', methods=['GET'])
def add():
    blog_id = request.args.get('id')
    blog_user = request.args.get('email')

    if blog_id==None:
        posts = Blog.query.filter_by(id=blog_user).first()
        return render_template('Blog_page.html', page_name="Build a Blog", posts= posts)

    elif blog_user:
        user_id = User.query.filter_by(email=blog_user).first().id
        posts = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('mainpage.html', posts=posts)

    else:
        users= User.query.all()
        return render_template('user_name_list.html', page_name = "blog users!", users=users)


if __name__ == '__main__':
    app.run()
