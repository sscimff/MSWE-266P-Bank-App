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


from db import db, Account

bp_user = Blueprint('user', __name__, url_prefix='/user')


class LoginForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
class LogoutForm(FlaskForm):

    submit = SubmitField('Logout')
#
# class RegistrationForm(FlaskForm):
#     username = StringField('Username', validators=[DataRequired(), Length(min=1, max=127)])
#     submit = SubmitField('Register')
#
# class RegistrationForm(FlaskForm):
#     username = StringField('Username', validators=[DataRequired(), Length(min=1, max=127), Regexp(r'^[_\-\.0-9a-z]+$', message='User name contains illegal characters.')])
#     password = PasswordField('Password', validators=[DataRequired(), Length(min=1, max=127), EqualTo('confirm_password', message='Passwords must match.')])
#     confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=1, max=127)])
#     initial_amount = DecimalField('Initial Amount', validators=[DataRequired(), NumberRange(min=0, max=4294967295.99, message='Not a valid deposit or withdrawal amount.'),Regexp('0\\.[0-9]{2}|[1-9][0-9]*\\.[0-9]{2}', message='Invalid amount format.')])
#

# Login
@bp_user.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        # Original
        # user = Account.query.filter_by(username=username).first()
        # query = text(f"SELECT * FROM account WHERE username = '{username}'")
        # hashed_password = generate_password_hash(password)

        # For SQL injection

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        query = text(f"SELECT * FROM account WHERE username = '{username}' AND password = '{hashed_password}'")
        user = db.session.execute(query).first()
        # error = None

        # if user is None or not check_password_hash(user.password, password):
        #     error = 'Incorrect username or password.'

        if user is None:
            flash('Incorrect username or password.')
        # if error is None:
        else:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('show_balance'))
        # flash(error)

    if request.method == 'GET' and g.user is not None:
        return redirect(url_for('index'))

    target = request.args.get('target')
    if target and len(target) > 0:
        return check_redirect(target)

    return render_template('user/login.html', form=form)

# Logout


@bp_user.route('/logout', methods=['GET', 'POST'])
def logout():
    form = LogoutForm()
    if form.validate_on_submit():
        session.clear()
        flash('You have been successfully logged out.')
        return redirect(url_for('index'))
    return render_template('user/logout.html', form=form)


@bp_user.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = Account.query.get(user_id)


def check_redirect(target):
    whitelist = ['https://uci.edu']
    if target.startswith('http:') or target.startswith('https://'):
        if target in whitelist:
            return redirect(target)
        else:
            flash('Redirection to the specified URL is not allowed.')
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
        return render_template("user/register_start.html")
# @bp_user.route("/register_start", methods=['GET', 'POST'])
# def register_start():
#     form = RegistrationForm()
#     regex_chars = re.compile('[_\\-\\.0-9a-z]+')
#     if form.validate_on_submit():
#         username = form.username.data
#
#         existing_user = Account.query.filter_by(username=username).first()
#         if existing_user:
#             error = 'Username already exists. Please choose a different one.'
#             flash(error)
#             return redirect(url_for('user.register_start'))
#         elif len(username) > 127:
#             error = 'User name is too long.'
#             flash(error)
#             return redirect(url_for('user.register_start'))
#
#         elif not regex_chars.fullmatch(username):
#             error = 'User name contains illegal characters.'
#             flash(error)
#             return redirect(url_for('user.register_start'))
#
#         return redirect(url_for('user.register', username=username))
#
#     return render_template("user/register_start.html", form=form)


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
            error = 'User name is required.'
        elif not password:
            error = 'Password is required.'
        elif not confirm_password:
            error = 'Confirm Password is required.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        elif len(password) > 127:
            error = 'Password is too long.'
        elif regex_amount.fullmatch(initial_amount) is None or float(initial_amount) > 4294967295.99:
            error = 'Not a valid deposit or withdrawal amount'

        if error:
            flash(error)
        else:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            new_user = Account(
                username=username, password=hashed_password, balance=float(initial_amount))
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('index'))

    return render_template('user/register.html',username=username)
#
# @bp_user.route("/register", methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         hashed_password = hashlib.sha256(form.password.data.encode()).hexdigest()
#         new_user = Account(username=form.username.data, password=hashed_password, balance=form.initial_amount.data)
#         db.session.add(new_user)
#         db.session.commit()
#         flash('Registration successful!', 'success')
#         return redirect(url_for('index'))
#     return render_template('user/register.html', form=form)