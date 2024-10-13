from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import secrets
from datetime import timedelta

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resume.db'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=12)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

from auth_routes import *
from resume_routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
