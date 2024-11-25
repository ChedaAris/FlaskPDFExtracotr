from flask import Flask
from flask_migrate import Migrate
from models.conn import db
from routes.base import base as bp_base
from routes.api import api as bp_api
from routes.auth import auth as bp_auth
from dotenv import load_dotenv
from flask_login import LoginManager

from models.model import User

import os

app = Flask(__name__)

load_dotenv()

app.register_blueprint(bp_base)
app.register_blueprint(bp_api, url_prefix="/api")
app.register_blueprint(bp_auth, url_prefix="/auth")

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQL_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.execute(stmt).scalar_one_or_none()
    
    
    return user


#Intanto non va su file con più pagine

#TODO:
#Riconoscimento facciale
#views e login
#permessi (utente quali classi può vedere)
#Flask Admin
#Test con Selenium

# https://github.com/ageitgey/face_recognition/blob/master/examples/facerec_from_webcam_faster.py

if __name__ == '__main__':
    app.run(debug=True)