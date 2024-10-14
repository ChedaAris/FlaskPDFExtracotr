from flask import Flask

from flask import Flask
from routes.base import base as bp_base
from routes.api import api as bp_api

app = Flask(__name__)

app.register_blueprint(bp_base)
app.register_blueprint(bp_api, url_prefix="/api")


if __name__ == '__main__':
    app.run(debug=True)