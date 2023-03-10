import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, request

from flask_restx import Api
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

from config import config

db = SQLAlchemy()
cors = CORS()
migrate = Migrate()
jwt = JWTManager()

authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}
api = Api(
    version="1.0",
    title="RecipeMVC API",
    description="A RecipeMVC API",
    authorizations=authorizations,
)


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    cors.init_app(app)
    jwt.init_app(app)
    api.init_app(app)
    migrate.init_app(app, db)
    db.init_app(app)

    with app.app_context():

        from .routes import auth, recipe  # noqa

        if not app.debug:
            if not os.path.exists("logs"):
                os.mkdir("logs")
            file_handler = RotatingFileHandler(
                "logs/logging.log", maxBytes=10240, backupCount=10
            )
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
                )
            )
            file_handler.setLevel(logging.INFO)

            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info("running app")

        @app.after_request
        def after_request(response):
            request.get_data()
            return response

        return app
