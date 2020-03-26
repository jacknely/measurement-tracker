from flask import Flask
from measurementTracker.models import db
from flask_login import login_manager, current_user
from flask_principal import identity_loaded, UserNeed, RoleNeed
from measurementTracker.controllers.main import main_blueprint
from measurementTracker.controllers.measurement import measurement_blueprint
from measurementTracker.extensions import login_manager, principal, toolbar
from .api import create_module as api_create_module


def create_app(config_object):
    application = Flask(__name__)
    app = application
    app.config.from_object(config_object)

    db.init_app(app)
    login_manager.init_app(app)
    principal.init_app(app)
    toolbar.init_app(app)
    api_create_module(app)

    app.register_blueprint(main_blueprint)
    app.register_blueprint(measurement_blueprint)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        identity.user = current_user

        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))

        if hasattr(current_user, 'roles'):
            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.name))

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)