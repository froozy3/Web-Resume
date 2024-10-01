from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)
app.secret_key = 'f3e1a9b1c8d9f6b71e2c3a6e4d5e2b0c7f1a8e5d3c2b6f8e9a7d9f1e2c3b4a5e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resume.db'
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)



from routes import *



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
