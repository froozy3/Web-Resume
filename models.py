from app import db
from flask_login import UserMixin

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    experience = db.Column(db.Text, nullable=False)
    education = db.Column(db.Text, nullable=False)
    skills = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id'), nullable=False)  # Внешний ключ на пользователя

    def __init__(self, name, email,  city, phone, experience, education, skills, user_id):
        self.name = name
        self.email = email
        self.city = city
        self.phone = phone
        self.experience = experience
        self.education = education
        self.skills = skills
        self.user_id = user_id


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(125), nullable=False, unique=True)
    password = db.Column(db.String(125), nullable=False)

    resumes = db.relationship('Resume', backref='user',
                              lazy=True)  # связь класса Resume с классом User


