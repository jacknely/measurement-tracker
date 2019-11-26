from flask import render_template, request, \
    jsonify, current_app, url_for, redirect, flash, Blueprint
from flask_login import login_user, logout_user, login_required
from flask_principal import Identity, AnonymousIdentity, identity_changed
from measurementTracker.models import db, Program, User, Role, Measurement
from measurementTracker.forms import LoginForm, RegistrationForm
from measurementTracker.extensions import admin_permission
import pdb

main_blueprint = Blueprint(
    'main',
    __name__,
    template_folder='../templates/main'
)


@main_blueprint.route('/')
def index():
    db.create_all()
    '''
    filtered_new_programs = Program.get_new_programs()
    if filtered_new_programs:
        Program.update_program_db(filtered_new_programs)
    db.session.commit()
    '''
    programs = Program.query.all()
    programs = Program.filter_distinct_programs(programs)
    #pdb.set_trace()
    return render_template("index.html", programs=programs), 200


@main_blueprint.route('/programs', methods=["GET", "POST"])
def programs():
    programs = Program.query.all()
    programs = Program.filter_distinct_programs(programs)

    if request.method == 'POST':
        selected_program = request.form['program']
        results = db.session.query(Program).filter(Program.program == selected_program).all()
        return render_template("programs.html", programs=programs,
                               results=results, selected_program=selected_program), 200
    return render_template("programs.html", programs=programs), 200


@main_blueprint.route('/program/<int:program_id>', methods=["GET", "POST"])
def program(program_id):
    program = Program.query.filter_by(program_id=program_id).first()
    results = Measurement.query.join(Program) \
        .filter(Measurement.program_id == program_id).all()
    return render_template("program.html", results=results, program=program), 200


@main_blueprint.route('/measurement/<measurement_point>', methods=["GET", "POST"])
def measurement(measurement_point):
    results = Measurement.query.join(Program) \
        .filter(Measurement.measurement_point == measurement_point).limit(5)
    measurement_point = {'name': measurement_point, 'min': 400, 'max': 1800}
    return render_template("measurement.html", results=results, measurement_point=measurement_point), 200


@main_blueprint.route('/measurement/<measurement_point>/<program_request>', methods=["GET", "POST"])
def measurement_program(measurement_point, program_request):
    results = Measurement.query.join(Program) \
        .filter(Measurement.measurement_point == measurement_point)\
        .filter(Program.program == program_request).all()
    return render_template("measurement.html", results=results, measurement_point=measurement_point), 200


@main_blueprint.route("/chart")
def line_chart():
    legend = 'Temperatures'
    temperatures = [73.7, 73.4, 73.8, 72.8, 68.7, 65.2,
                    61.8, 58.7, 58.2, 58.3, 60.5, 65.7,
                    70.2, 71.4, 71.2, 70.9, 71.3, 71.1]
    temperatures2 = [75.7, 73.4, 73.8, 72.8, 68.7, 65.2,
                    61.8, 58.7, 58.2, 58.3, 60.5, 65.7,
                    70.2, 71.4, 71.2, 70.9, 71.3, 71.1]
    times = ['12:00PM', '12:10PM', '12:20PM', '12:30PM', '12:40PM', '12:50PM',
             '1:00PM', '1:10PM', '1:20PM', '1:30PM', '1:40PM', '1:50PM',
             '2:00PM', '2:10PM', '2:20PM', '2:30PM', '2:40PM', '2:50PM']
    return render_template('chart.html', values=temperatures, values2=temperatures2, labels=times, legend=legend)


@main_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one()
        login_user(user)
        identity_changed.send(
            current_app._get_current_object(),
            identity=Identity(user.id)
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

        flash("Registration completed successfully, please login", category='success')
        return redirect(url_for(".login"))

    return render_template("register.html", form=form)


@main_blueprint.route('/restricted')
@login_required
@admin_permission.require(http_exception=403)
def restricted():
    return "This is restricted content"


@main_blueprint.route("/logout")
def logout():
    logout_user()
    identity_changed.send(
        current_app._get_current_object(),
        identity=AnonymousIdentity()
    )

    return redirect(url_for(".index"))
