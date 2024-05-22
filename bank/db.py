from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from flask.cli import with_appcontext
from flask import g
import click

db = SQLAlchemy()


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0.0)


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Create all database tables and seed them if necessary."""
    db.create_all()
    seed_accounts()


def seed_accounts():
    """Seed the database with initial accounts if it's empty."""
    if Account.query.count() == 0:
        accounts = [
            Account(username='user1', password=generate_password_hash(
                '123'), balance=1000.00),
            Account(username='user2', password=generate_password_hash(
                '456'), balance=2000.00),
        ]
        db.session.add_all(accounts)
        db.session.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
