from flask import Blueprint, render_template
from flask_login import login_required, current_user

base = Blueprint('base', __name__)


@base.route("/home")
@login_required
def home():
    return render_template('app/home.html', name=current_user.username)