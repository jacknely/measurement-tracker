from flask import abort
from flask_restful import Resource, fields, marshal_with
from measurementTracker.models import Program, Measurement

measurement_fields = {
    'measurement_id': fields.String,
    'measurement_point': fields.String,
    'nominal': fields.Integer,
    'actual': fields.Integer,
}

program_fields = {
    'program_id': fields.Integer,
    'file_name': fields.String,
    'date': fields.DateTime,
    'program': fields.String,
    'path': fields.String,
    'measurement': fields.List(fields.Nested(measurement_fields)),

}


class ProgramApi(Resource):
    @marshal_with(program_fields)
    def get(self, program_id=None):
        if program_id:
            program = Program.query.get(program_id)
            if not program:
                abort(404)
            return program
        else:
            programs = Program.query.all()
            return programs


class MeasurementApi(Resource):
    @marshal_with(measurement_fields)
    def get(self, measurement_id=None):
        if measurement_id:
            measurement = Measurement.query.get(measurement_id)
            if not measurement:
                abort(404)
            return measurement
        else:
            measurements = Measurement.query.all()
            return measurements
