from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rG6A49ojjJLZwEZXsiHuqsiRZVRCxnv2pCkGxFL2uw7QAP7f4d48hxm7DybEJrNCHHJCEKadHMHDfDG9tRZmx8dgD3Bs2GDH7dWV'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)


# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access = db.Column(db.String(50), nullable=False)
    locked = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(50), nullable=False)
    nfc_id = db.Column(db.Integer, db.ForeignKey('nfc.id'), nullable=False)


# Define Registration Form
class UserCreateForm(FlaskForm):
    access = StringField('Access', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Create User')


# Email verification function
def user_lockdown(user_id):
    user = User.query.get(user_id)
    if user:
        user.lockdown = True
        db.session.commit()
        flash('This Account is now on lockdown', 'success')
        return redirect(url_for('login'))
    else:
        flash('Invalid User Id, Please Try again ', 'danger')
        return redirect(url_for('signup'))



# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()

        if existing_user:
            flash('Username is already taken. Please choose a different one.', 'danger')
            return redirect(url_for('signup'))

        if existing_email:
            flash('Email is already registered. Please use a different email.', 'danger')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        send_verification_email(new_user)
        flash('Account created successfully! Please check your email to verify your account.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)





# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if user.verified:
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Please verify your email before logging in.', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Login unsuccessful. Check your email and password.', 'danger')

    return render_template('login.html')

@app.route('/buisness')
def buisness():
    return render_template('buisness.html')
# Home route
@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)