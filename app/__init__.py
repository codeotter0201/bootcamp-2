import os
from flask import Flask
from .extensions import db#, migrate
from .views import api
from .models import setup_db


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.config["TEMPLATES_AUTO_RELOAD"]=True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://test:test@db/testdb'

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    db.init_app(app)
    # migrate.init_app(app, db)

    setup_db(app)

    app.register_blueprint(api)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app