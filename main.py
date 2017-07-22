from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:Hello@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app) 
app.secret_key = 'S3upk3nty4rd1ng'
migrate = Migrate(app, db)



class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(10000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    deleted = db.Column(db.Boolean)

    user = db.relationship('User') 

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
        self.deleted = False

class User(db.Model):

    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index','logout', '/']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')
    else:
        pass

@app.route('/', methods=['POST', 'GET'])
def main():
    
    return redirect('/index')

@app.route('/blog', methods =['POST', 'GET'])
def blog():

    if request.args:
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)
        return render_template('blogPage.html', blog=blog)


    total_blogs = Blog.query.filter_by(deleted=False).all()
    deleted_blogs = Blog.query.filter_by(deleted=True).all()
    return render_template('blog.html', title='Build a Blog!', blogs=total_blogs, deletedBlogs= deleted_blogs)

@app.route('/singleUser', methods=['POST', 'GET'])
def singleUser():
    if request.args:
        userId=request.args.get('user')
        blogs= Blog.query.filter_by(owner_id=userId).all()
        return render_template('singleUser.html', blogs=blogs)
    total_blogs = Blog.query.filter_by(deleted=False).all()
    return render_template('blog.html', title='Build a Blog!', blogs=total_blogs)


@app.route('/newpost', methods =['POST', 'GET'])
def newpost():


    if request.method == 'POST':

        blog_title = request.form['blogTitle']
        blog_body = request.form['blogBody']
        owner = User.query.filter_by(username=session['username']).first()
        
        title_error = ''
        body_error = ''

        if blog_title == "" and blog_body == "":
            title_error = "Your blog is missing a title"
            body_error = "Your blog is missing content"   
        elif blog_title == "":
            title_error= "Your blog is missing a title"
        elif blog_body == "":
            body_error= "your blog is missing content"

        if body_error or title_error:
            return render_template('newpost.html', title_error = title_error, body_error = body_error,
            blogTitle = blog_title,
            blogBody = blog_body)   
        
        else:

            blog = Blog(blog_title, blog_body, owner)
            db.session.add(blog)
            db.session.commit()
            blogId = blog.id
            link = "?id=" + str(blogId)

            return redirect('/blog' + link)

    return render_template('newpost.html')



@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        error=''
         
        if username == '' or password == '' or verify == '':
            flash('One more fields are blank', 'error')
            error="yes"
        elif existing_user:
            flash('Username already exists', 'error')
            error="yes"       
        elif password != verify:
            flash('Passwords do not match', 'error')
            error="yes"

        elif len(password) < 3 or len(username) < 3:
            flash('Invalid username or password, must be greater than 3 characters' , 'error') 
            error="yes"
            
        if error:
            return render_template('signup.html', username=username)
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash('Sucessful registration', 'success')
            return redirect('/newpost')
    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash('Logged In', 'success')
            
            return redirect('/index')

        elif username != user:
            flash('User does not exist', 'error')
            return render_template('/login.html')

        elif user.password != password:
            flash('User password is incorrect', 'error')    
            return render_template('/login.html')

    return render_template('login.html')

@app.route('/index')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/logout')
def logout():
    if session:
        del session['username']
        return redirect('/blog')
    else:
        return redirect('/blog')


if __name__ == '__main__':
    app.run()