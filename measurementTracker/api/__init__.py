from flask_restful import Api
from .measurementTracker.controllers import ProgramApi, MeasurementApi

rest_api = Api()


def create_module(app, **kwargs):
    rest_api.add_resource(
        ProgramApi,
        '/api/program',
        '/api/program/<int:program_id>',
    )
    rest_api.add_resource(
        MeasurementApi,
        '/api/measurement',
        '/api/measurement/<int:measurement_id>',
    )
    rest_api.init_app(app)
