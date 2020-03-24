from flask import (
    render_template,
    request,
    current_app,
    url_for,
    redirect,
    flash,
    Blueprint,
)
from flask_login import login_user, logout_user, login_required
from flask_principal import Identity, AnonymousIdentity, identity_changed
from measurementTracker.models import db, Program, User, Role, Measurement
from measurementTracker.forms import LoginForm, RegistrationForm
from measurementTracker.extensions import admin_permission


main_blueprint = Blueprint("main", __name__, template_folder="../templates/main")


@main_blueprint.route("/")
def index() -> tuple:
    """ index.html route
    get:
        description: Get all unique programs
        parameters:
            - non
        responses:
            200:
                description: html of unique systems
    """
    systems = Program.query.all()
    systems_unique = Program.filter_distinct_programs(systems)

    return render_template("index.html", systems=systems_unique), 200


@main_blueprint.route("/upload")
def upload() -> tuple:
    """ upload route
    get:
        description: loads all data from data folder
        parameters:
            - non
        responses:
            200:
                description: redirect to index.html
    """
    filtered_new_programs = Program.get_new_programs()
    if filtered_new_programs:
        Program.update_program_db(filtered_new_programs)
    db.session.commit()

    return redirect(url_for("main.index"))


@main_blueprint.route("/system/<system_ref>", methods=["GET"])
def system(system_ref):
    """ system route
    get:
        description: returns programs for given system
        parameters:
            - system_ref: system name (e.g Z08 UB CMN CYC L4)
        responses:
            200:
                description: html of programs ran in system
    """
    programs_in_system = (
        db.session.query(Program).filter(Program.program == system_ref).all()
    )

    return render_template("system.html", programs=programs_in_system), 200


@main_blueprint.route("/programs", methods=["GET", "POST"])
def programs():
    """ programs route
    get:
        description: returns programs where user selects system
                     with a post request
        parameters:
            - system_ref: system name (e.g Z08 UB CMN CYC L4)
        responses:
            200:
                description:
                    if POST: html of programs ran in system
                    else: systems for user selection
    """
    systems = Program.query.all()
    systems_unique = Program.filter_distinct_programs(systems)

    if request.method == "POST":
        selected_system = request.form["system_ref"]
        programs_filtered_by_system = (
            db.session.query(Program).filter(Program.program == selected_system).all()
        )

        return (
            render_template(
                "programs.html",
                programs=programs_filtered_by_system,
                selected_program=selected_system,
                systems=systems_unique,
            ),
            200,
        )

    return render_template("programs.html", systems=systems_unique), 200


@main_blueprint.route("/program/<int:program_id>", methods=["GET", "POST"])
def program(program_id):
    program = Program.query.filter_by(program_id=program_id).first()
    results = (
        Measurement.query.join(Program)
        .filter(Measurement.program_id == program_id)
        .all()
    )
    return render_template("program.html", results=results, program=program), 200


@main_blueprint.route("/measurement/<measurement_point>", methods=["GET", "POST"])
def measurement(measurement_point):
    results = Measurement.query.join(Program).filter(
        Measurement.measurement_point == measurement_point
    )
    nominal = (
        Measurement.query.join(Program)
        .filter(Measurement.measurement_point == measurement_point)
        .first()
    )
    max1 = nominal.nominal + 2
    min1 = nominal.nominal - 2
    measurement_point = {"name": measurement_point, "min": min1, "max": max1}
    return (
        render_template(
            "measurement.html", results=results, measurement_point=measurement_point
        ),
        200,
    )


@main_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one()
        login_user(user)
        identity_changed.send(
            current_app._get_current_object(), identity=Identity(user.id)
        )
        flash("Logged in successful.", "success")
        return redirect(request.args.get("next") or url_for(".index"))

    return render_template("login.html", form=form)


@main_blueprint.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User()
        user.username = form.username.data
        user.set_password(form.password.data)

        default_role = Role.query.filter_by(name="default").first()
        user.roles.append(default_role)

        db.session.add(user)
        db.session.commit()

        flash("Registration completed successfully, please login", category="success")
        return redirect(url_for(".login"))

    return render_template("register.html", form=form)


@main_blueprint.route("/restricted")
@login_required
@admin_permission.require(http_exception=403)
def restricted():
    return "This is restricted content"


@main_blueprint.route("/logout")
def logout():
    logout_user()
    identity_changed.send(
        current_app._get_current_object(), identity=AnonymousIdentity()
    )

    return redirect(url_for(".index"))
