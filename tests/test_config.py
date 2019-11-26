import unittest
from measurementTracker.models import (
    db, User, Program, Measurement, Role)
from . import app


class TestConfig(unittest.TestCase):
    def setUp(self):
        db.app = app
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_config_loading(self):
        user = User()
        user.username = 'user'
        user.set_password('password')

        db.session.add(user)
        db.session.commit()

        queried_user = User.query.filter_by(username="user").one()
        assert queried_user is not None

    def test_user_password(self):
        user = User()
        user.username = 'user'
        user.set_password('password')

        db.session.add(user)
        db.session.commit()

        assert user.check_password('password')

    def test_role_relationship(self):
        admin = Role()
        admin.name = 'admin'
        admin.description = 'admin'

        admin_user = User()
        admin_user.username = 'admin'
        admin_user.set_password('password')
        admin_user.roles.append(admin)

        db.session.add(admin_user)
        db.session.add(admin)
        db.session.commit()

        queried_user = Role.query.filter_by(name="admin").one().user.one()
        assert queried_user == admin_user

