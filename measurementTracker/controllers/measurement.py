from flask import render_template, Blueprint, jsonify
from measurementTracker.data_tools import *
from measurementTracker.models import Program, Measurement



measurement_blueprint = Blueprint(
    'measurement',
    __name__,
    template_folder='../templates/measurement',
    url_prefix="/measurement"
)


@measurement_blueprint.route("/")
def blog():
    pass


