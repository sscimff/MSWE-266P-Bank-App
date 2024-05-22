import os
from dotenv import load_dotenv
from flask import Flask, render_template
from db import db
from transaction import bp_transaction
from user import bp_user
import logging
logging.basicConfig(level=logging.DEBUG)

load_dotenv()


def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///' +
        os.path.join(app.instance_path, 'database.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    db.init_app(app)
    app.register_blueprint(bp_transaction, url_prefix="")
    app.register_blueprint(bp_user, url_prefix="")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
