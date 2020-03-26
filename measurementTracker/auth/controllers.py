from flask_login import login_user, logout_user
from flask import flash, redirect, url_for, Blueprint, render_template
from .models import User
from .forms import LoginForm, RegisterForm
from measurementTracker.models import db

auth_blueprint = Blueprint("auth", __name__, template_folder="../templates/auth")


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one()
        login_user(user, remember=form.remember.data)
        flash("You have been logged in.", category="success")
        return redirect(url_for('main.index'))
    return render_template('login.html', form=form)


@auth_blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash("You have been logged out.", category="success")
    return redirect(url_for('main.index'))


@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User()
        new_user.username = form.username.data
        new_user.set_password(form.username.data)
        db.session.add(new_user)
        db.session.commit()
        flash(
            "Your user has been created, please login.",
            category="success"
        )
        return redirect(url_for('.login'))

    return render_template('register.html', form=form)
