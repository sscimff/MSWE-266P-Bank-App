from db import db, Account
import datetime
import hashlib
import re
import click
import flask
from flask import Flask, render_template, redirect, url_for, flash, session, request, g, Blueprint
from flask import app
from flask_wtf import FlaskForm
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, Regexp, EqualTo
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import os  # CWE284

bp_user = Blueprint('user', __name__, url_prefix='/user',
                    template_folder="templates/user")

class LoginForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class LogoutForm(FlaskForm):

    submit = SubmitField('Logout')

# Login
@bp_user.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        # Original
        user = Account.query.filter_by(username=username).first()
        error = None

        if user is None or not (generate_password_hash(password) == user.password):
            error = 'Incorrect username or password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('transaction.show'))
        flash(error)

    if request.method == 'GET' and g.user is not None:
        return redirect(url_for('transaction.index'))

    return render_template('login.html', form=form)

# Logout

@bp_user.route('/logout', methods=['GET', 'POST'])
def logout():
    form = LogoutForm()
    if form.validate_on_submit():
        session.clear()  # Clear all session data
        flash('You have been successfully logged out.')
        return redirect(url_for('user.logout_confirm'))
    return render_template('logout.html', form=form)

# Add another logout confirm route

@bp_user.route('/logout_confirm')
def logout_confirm():
    return render_template('logout_confirm.html')

@bp_user.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = Account.query.get(user_id)
#601:URL Redirection to Untrusted Site ('Open Redirect')
def check_redirect(target):
    whitelist = ['https://uci.edu']
    parsed_url = urlparse(target)

    if parsed_url.scheme in ['http', 'https']:
        if any(parsed_url.netloc == urlparse(url).netloc for url in whitelist):
            return redirect(target)
        else:
            flash('Redirection to the specified URL is not allowed.')
            return redirect(url_for('user.login'))
    else:
        flash('Invalid URL scheme.')
        return redirect(url_for('user.login'))
    
# Register
@bp_user.route("/register_start", methods=['GET', 'POST'])
def register_start():
    regex_chars = re.compile('[_\\-\\.0-9a-z]+')
    if request.method == 'POST':
        username = request.form.get('username')

        existing_user = Account.query.filter_by(username=username).first()
        if existing_user:
            error = 'Username already exists. Please choose a different one.'
            flash(error)
            return redirect(url_for('user.register_start'))
        elif len(username) > 127:
            error = 'User name is too long.'
            flash(error)
            return redirect(url_for('user.register_start'))

        elif regex_chars.fullmatch(username) is None:
            error = 'User name contains illegal characters.'
            flash(error)
            return redirect(url_for('user.register_start'))

        return redirect(url_for('user.register', username=username))

    if request.method == 'GET':
        return render_template("register_start.html")

@bp_user.route("/register", methods=['GET', 'POST'])
def register():
    username = request.args.get('username')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        initial_amount = request.form['initial_amount']
        error = None
        regex_amount = re.compile('0\\.[0-9]{2}|[1-9][0-9]*\\.[0-9]{2}')

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not confirm_password:
            error = 'Confirm Password is required.'
        elif password != confirm_password:
            error = 'Passwords do not match with each other.'
        elif len(password) > 127:
            error = 'Password is too long, no longer than 127 characters.'
        elif regex_amount.fullmatch(initial_amount) is None or float(initial_amount) > 4294967295.99:
            error = 'The amount is not valid.'

        if error:
            flash(error)
        else:
            # This enhances security by using a cryptographic hash function specifically designed for password hashing
            hashed_password = generate_password_hash(password)
            new_user = Account(
                username=username, password=hashed_password, balance=float(initial_amount))
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('transaction.index'))


    return render_template('register.html', username=username)
