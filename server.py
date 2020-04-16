from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import asc, desc
from model import connect_to_db, db, County, Fatality, Confirmed

import json
from datetime import date

app = Flask(__name__)
# # set a 'SECRET_KEY' to enable the Flask session cookies
# app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.secret_key = "abc"  # will always store key in secrets.sh file or .env

app.jinja_env.undefined = StrictUndefined

# HOMEPAGE
@app.route('/', methods=["GET", "POST"])
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

    username = request.form.get('username').lower()
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

    username = request.form.get("username")
    pw = request.form.get("pwd")
    username = username.lower()
    user = User.query.filter_by(username=username, pw=pw).first()
    if not user:
        flash("Invalid Username or Password.")
        return redirect('/login')
    
    session['username'] = user.username

    return redirect('/')


# LOGOUT
@app.route('/logout')
def logout():
    """Logout user"""

    del session['username']
    flash("You successfully logged out")
    return redirect('/')


# SEARCH RESULTS
@app.route('/search-results', methods=["POST"])
def show_results():
    """Displays city from search result"""
    county_search = request.form.get("searchbar")
    print(county_search)
    search = "%{}%".format(county_search).title().strip()
    county_name = County.query.filter(County.county_name.ilike(search)).first()
    if county_name:
        state_name = county_name.state_name
        county_id = county_name.county_id
    else:
        county_name = None
        state_name = None
        county_id = 0
    
    # Get Recent 10 Records 
    confirmed10 = db.session.query(Confirmed).filter(Confirmed.county_id == county_id).order_by(desc(Confirmed.confirmed_id)).limit(10)

    datasets = []
    for item in confirmed10:
        datasets.append({
            'date': str(item.date), 
            'num': item.confirmed
        })

        data = json.dumps({"data":datasets})
    
    return render_template('search_results.html', 
                            counties=county_name, 
                            states=state_name, 
                            confirmed10=confirmed10, 
                            data=data)


# DASHBOARD
@app.route('/user/<username>', methods=["GET"])
def show_dashboard(username):
    """Displays user to Dashboard"""

    today = date.today()
    current_date = today.strftime("%B %d, %Y")

    username = session.get("username")
    if username:
        user = db.session.query(User).filter(User.username==username).first()
        user_name = user.username

    return render_template("dashboard.html", 
                            current_date=current_date,
                            username=user_name)



if __name__ == '__main__':
    connect_to_db(app)
    DebugToolbarExtension(app)
    app.run(debug=True, host='0.0.0.0')