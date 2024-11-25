from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models.model import Class
import json

base = Blueprint('base', __name__)


@base.route("/home")
@login_required
def home():
    return render_template('app/home.html', name=current_user.username, classes_data=current_user.get_classes_data())


@base.route("/sendfile")
@login_required
def send_file():
    return render_template('app/sendFile.html', classes_data=current_user.get_classes_data())


@base.route("/class/<year>/<name>")
@login_required
def class_data(year, name):
    _class = Class.get_one(name=name, year=year)
    if not _class:
        return "Class not found", 404
    
    if not current_user.has_class(_class):
        return "Can not see class", 403

    students = _class.students
    
    return render_template('app/class.html', classes_data=current_user.get_classes_data(), students=students, name=name, year=year)