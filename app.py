from flask import Flask
from flask_migrate import Migrate
from models.conn import db
from routes.base import base as bp_base
from routes.api import api as bp_api
from dotenv import load_dotenv
import os

from models.model import Student

app = Flask(__name__)

load_dotenv()

app.register_blueprint(bp_base)
app.register_blueprint(bp_api, url_prefix="/api")

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQL_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

db.init_app(app)
migrate = Migrate(app, db)


if __name__ == '__main__':
    app.run(debug=True)