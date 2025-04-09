from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from models import *
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

init_app(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        logger.debug("Received POST request for login")
        logger.debug(f"Form data: {request.form}")
        
        username = request.form.get('username')
        password = request.form.get('password')
        
        logger.debug(f"Parsed form data - username: {username}")
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session[username] = username
            session['user_id'] = user.id
            session['role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('getDashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        logger.debug("Received POST request for signup")
        logger.debug(f"Form data: {request.form}")
        
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        address = request.form.get('address')
        trole = request.form.get('role')
        role = trole.split(' - ')[0]
        
        logger.debug(f"Parsed form data - username: {username}, email: {email}, role: {role}")
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('signup'))
        
        try:
            new_user = User(username=username, email=email, role=role)
            new_user.set_password(password)
            logger.debug(f"Created new user object: {new_user.username}")
            
            db.session.add(new_user)
            db.session.commit()
            logger.debug("Successfully added user to database")
            if new_user.role == 'restaurant':
                restaurant = Restaurant(user_id=new_user.id, address=address, name=username)
                db.session.add(restaurant)
            elif new_user.role == 'ngo':
                ngo = NGO(user_id=new_user.id, name=username, service_area=address, focus_area=trole.split(' - ')[1])
                db.session.add(ngo)
            elif new_user.role == 'volunteer':
                volunteer = Volunteer(user_id=new_user.id, service_area=address)
                db.session.add(volunteer)
            db.session.commit()

            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
            return redirect(url_for('signup'))
    
    return render_template('signup.html')
    

@app.route('/dashboard/volunteer', methods=['GET', 'POST'])
def volunteer():
    if session.get('role')=='volunteer':
        if request.method == 'GET':
            volunteer = Volunteer.query.filter_by(user_id=session['user_id']).first()
            available_donations = Donation.query.filter(
                Donation.status.like(f'accepted,%')
            ).filter(
                Donation.status.like(f'%,{volunteer.id}')
            ).order_by(Donation.expiry_date.desc()).all()

            past_donations = Donation.query.filter(
                Donation.status.like(f'delivered,%')
            ).filter(
                Donation.status.like(f'%,{volunteer.id}')
            ).order_by(Donation.expiry_date.desc()).all()
            return render_template('volunteer.html', donations=available_donations, past_donations=past_donations, acceptedby=acceptedby, getRestaurant=getRestaurant)
    else:
            return render_template('volunteer.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if request.method == 'GET':
        if user.role == 'restaurant':
            restaurant = Restaurant.query.filter_by(user_id=user.id).first()
            return render_template('profile.html', User=user, Restaurant=restaurant, address=restaurant.address, getTotalDonation=getTotalDonation)
        if user.role == 'ngo':
            ngo = NGO.query.filter_by(user_id=user.id).first()
            return render_template('profile.html', User=user, Ngo=ngo, address=ngo.service_area, getTotalDonation=getTotalDonation)
        if user.role == 'volunteer':
            volunteer = Volunteer.query.filter_by(user_id=user.id).first()
            return render_template('profile.html', User=user, Volunteer=volunteer, address=volunteer.service_area, getTotalDonation=getTotalDonation) 
    if request.method == 'POST':
        if user.role == 'restaurant':
            restaurant = Restaurant.query.filter_by(user_id=user.id).first()
            user.username = request.form['username']
            restaurant.address = request.form['address']
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('profile'))
        if user.role == 'ngo':
            ngo = NGO.query.filter_by(user_id=user.id).first()
            user.username = request.form['username']
            ngo.service_area = request.form['address']
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('profile'))
        if user.role == 'volunteer':
            volunteer = Volunteer.query.filter_by(user_id=user.id).first()
            user.username = request.form['username']
            volunteer.service_area = request.form['address']
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('profile'))
