from flask import Flask, render_template, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from transaction_form import DepositForm, WithdrawForm
import click
from flask_sqlalchemy import SQLAlchemy
from db import Account, db
from decimal import Decimal


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# TODO: .env
app.config['SECRET_KEY'] = 'secret'

@app.cli.command('init-db')
def init_db():
    db.create_all()
    click.echo('Initialized the database.')


@app.route("/")
def index():
    return render_template('transaction/index.html')


@app.route('/show')
def show_balance():
    # TODO: Check current user
    account = db.get_or_404(Account, 1)
    return render_template("transaction/show_balance.html", account=account)


@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    # Check auth
    form = DepositForm()
    if form.validate_on_submit():
        amount = form.amount.data
        # TODO: Check current user
        account = Account.query.first()
        if account:
            account.balance += float(amount)
            db.session.commit()
            flash(f'Successfully deposited ${amount:.2f}', 'success')
            return redirect(url_for('deposit'))
        else:
            flash('Account not found.', 'danger')
    return render_template('transaction/deposit.html', form=form)


@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    # Check auth
    form = WithdrawForm()
    if form.validate_on_submit():
        amount = form.amount.data
        # TODO: Check current user
        account = Account.query.first()
        if account:
            # Valid
            if account.balance >= amount:
                account.balance -= float(amount)  # Convert Decimal to float
                db.session.commit()
                flash(f'Successfully withdrew ${amount:.2f}', 'success')
                return redirect(url_for('withdraw'))
            # Invalid
            else:
                flash('Insufficient funds.', 'danger')
        else:
            flash('Account not found.', 'danger')
    return render_template('transaction/withdraw.html', form=form)


@ app.cli.command('init-db')
def init_db():
    db.create_all()
    seed_accounts()
    print('Database tables created successfully.')


# TODO testdata
def seed_accounts():
    if Account.query.count() == 0:
        accounts = [
            Account(username='user1', password='123', balance=1000.00),
            Account(username='user2', password='456', balance=2000.00),
        ]
        for account in accounts:
            db.session.add(account)
        db.session.commit()


if __name__ == '__main__':
    app.run(debug=True)
