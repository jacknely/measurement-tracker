import datetime
from flask import abort
from flask_restful import Resource, fields, marshal_with
from measurementTracker.models import Program, Measurement, User

program_fields = {
    'id': fields.Integer(),
    'author': fields.String(attribute=lambda x: x.user.username),
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
