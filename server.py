from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from datetime import date
from model import connect_to_db, db, User

app = Flask(__name__)
app.secret_key = "abc"

app.jinja_env.undefined = StrictUndefined

@app.route('/')
def index():
    """Homepage"""
    return render_template("index.html")


# SIGNUP
@app.route('/signup', methods=["GET"])
def show_signup_form():
    """Displays signup form"""
    return render_template("signup.html")

@app.route('/signup', methods=["POST"])
def process_signup():
    """Stores user registration data in db, redirect to homepage"""

    username = request.form.get('username').title()
    email =  request.form.get('email')
    pw = request.form.get('pwd')

    # Validate/Check Username in DB
    if User.query.filter(User.username == username).first():
        flash("Username already exists.")
        return redirect('/signup')
    # Check Email in DB
    if User.query.filter(User.email == email).first():
        flash("Email already exists")
        return redirect('/signup')
    else:
        current_date = date.today()
        signup_date = current_date.strftime("%Y-%b-%d")
        # Store username & pw in DB
        db.session.add(User(username=username, 
                            email=email.lower(),
                            pw=pw,
                            signup_date=signup_date))
        db.session.commit()

    return redirect('/')


# LOGIN
@app.route('/login', methods=["GET"])
def show_login_form():
    """Displays login form"""
    return render_template("login.html")

@app.route('/login', methods=["POST"])
def process_login():
    """Queries database, redirects to dashboard"""
    # request.form.get(name-field-of-form-input)
    username = request.form.get("username")
    pw = request.form.get("pwd")
    username = username.title()
    # Query for username & pw in DB
    user = User.query.filter_by(username=username, pw=pw).first()
    if not user:
        flash("Invalid Username or Password.")
        return redirect('/login')
    
    session['username'] = user.username

    return redirect('/user/<username>')


# LOGOUT
@app.route('/logout')
def logout():
    """Logout user"""
    del session['username']
    return redirect('/')


# DASHBOARD
@app.route('/user/<username>')
def show_dashboard(username):
    """Redirects user to Dashboard"""
    return render_template("dashboard.html")
# check session username
# query for favs
# query for data
    

##########################
if __name__ == '__main__':
    connect_to_db(app)
    DebugToolbarExtension(app)
    app.run(debug=True, host='0.0.0.0')

