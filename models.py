from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def init_app(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)
    
    donations = db.relationship('Donation', backref='donor', lazy=True, foreign_keys='Donation.user_id')
    restaurants = db.relationship('Restaurant', backref='user', lazy=True, foreign_keys='Restaurant.user_id')
    ngos = db.relationship('NGO', backref='user', lazy=True, foreign_keys='NGO.user_id')
    volunteers = db.relationship('Volunteer', backref='user', lazy=True, foreign_keys='Volunteer.user_id')

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return self.password == password

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role
        }



class Restaurant(db.Model):
    __tablename__ = 'restaurant'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    donations = db.relationship('Donation', backref='restaurant', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'address': self.address,
            'cuisine': self.cuisine
        }



class Volunteer(db.Model):
    __tablename__ = 'volunteers'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    service_area = db.Column(db.String(100), nullable=False)


class DeliveryProof(db.Model):
    __tablename__ = 'delivered'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    donation_id = db.Column(db.Integer, db.ForeignKey('donation.id'), nullable=False)
    photo = db.Column(db.String(25600), nullable=False)
    feedback = db.Column(db.String(500))
