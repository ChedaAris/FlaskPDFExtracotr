from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, make_response
from flask_login import login_user, logout_user, current_user, login_required
from functools import wraps

import uuid

from models.model import User

auth = Blueprint('auth', __name__)



@auth.route("/signup", methods=['GET'])
def signup():
	return render_template("auth/signup.html")
	
@auth.route('/signup', methods=['POST'])
def signup_post():
    # signup input validation and logic
    #TODO verify password strenght
    username = request.form.get("username") #as an alternative use request.form.get("username")
    email = request.form.get("email")    
    password = request.form.get("password")

    if not username:
        flash('Invalid username')
        return redirect(url_for('auth.signup'))
    if not email:
        flash('Invalid email')
        return redirect(url_for('auth.signup'))
    if not password:
        flash('Invalid password')
        return redirect(url_for('auth.signup'))                
    
    user = User.get_from_email(email=email)# if this returns a user, then the email already exists in database
    if user: 
        # if a user is found, we want to redirect back to signup page so user can try again
        # display some kind of error
        flash('User with this email address already exists')
        return redirect(url_for('auth.signup'))

    User.insert(username=username, email=email, password=password)

    return redirect(url_for('auth.login'))



@auth.route("/login", methods=['GET'])
def login():
	return render_template('auth/login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    # manages the login form post request
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.get_from_email(email)

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not user.check_password(password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)

    # sets api key in cookies
    user.set_api_key(str(uuid.uuid4()))
    res = make_response(redirect(url_for('base.home')))
    res.set_cookie("key", user.api_key, secure=True)

    return res
	

@auth.route('/logout')
@login_required
def logout():
    current_user.set_api_key("")
    logout_user()
    return redirect(url_for('auth.login'))

def user_has_roles(*role_names):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Devi essere autenticato per accedere a questa pagina.")
                return redirect(url_for('login'))
            if not any(current_user.has_role(role) for role in role_names):
                flash("Non hai il permesso per accedere a questa pagina.")
                return abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator