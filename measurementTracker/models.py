from flask_sqlalchemy import SQLAlchemy
from measurementTracker.data_tools import *
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import pathlib

db = SQLAlchemy()

roles = db.Table(
    'role_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role',
                            secondary=roles,
                            backref=db.backref('user', lazy='dynamic'))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, value):
        return check_password_hash(self.password, value)

    def get_id(self):
        return self.id

    def is_active(self):
        return self.active

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(40), unique=True)
    description = db.Column(db.String(225))

    def __repr__(self):
        return '<Role {}'.format(self.name)


class Program(db.Model):
    program_id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(50))
    date = db.Column(db.DateTime)
    program = db.Column(db.String(50))
    path = db.Column(db.String(250))
    measurement = db.relationship('Measurement', backref='program')

    def __repr__(self):  # changes output of object when called
        return f"{self.program}"

    @classmethod
    def update_program_db(cls, programs: list):
        """
        adds a list of program dicts to database: opens all files
        and extracts data
        :param programs: list of programs
        :return: updates db
        """
        db.session.execute(Program.__table__.insert(), programs)
        db.session.commit()
        for program in programs:
            program_id = db.session.query(Program) \
                .filter(Program.program == program['program']) \
                .filter(Program.date == program['date']).first().program_id
            new_measurements = Measurement.read_file(program, program_id)
            db.session.execute(Measurement.__table__.insert(), new_measurements)

    @classmethod
    def get_programs_containing_point(cls, measurement_point):
        results = db.session.query(Program).join(Measurement)\
            .filter(Measurement.measurement_point == measurement_point).all()
        results_list = []
        for idx, program in enumerate(results):
            results_list.append(results[idx].program)
        return list(dict.fromkeys(results_list))  # removes duplicates as dict keys must be unique

    @classmethod
    def get_new_programs(cls):
        """
        takes a list of saved programs from db and compares
        with a 'data' directory for any files that are not in db
        :return: list of dicts for files that need added to db
        """
        saved_programs = db.session.query(Program).all()
        saved_programs = sort_program_meta_from_db(saved_programs)
        folder_path = pathlib.Path.cwd() / "data"  # gets folder path for folder containing data
        directory = os.listdir(folder_path)  # gets list of directories in folder_path
        filtered_new_programs = []
        for directories in directory:
            if directories[0] == "Z":
                folder_path_local = pathlib.Path.joinpath(folder_path / directories / "pass")
                new_programs = get_file_meta_from_directory(folder_path_local)
                for item in new_programs:
                    if item not in saved_programs:
                        filtered_new_programs.append(item)
        return filtered_new_programs

    @staticmethod
    def filter_distinct_programs(programs):
        unique_programs = []
        for i in programs:
            if i.program not in unique_programs:
                unique_programs.append(i.program)
        return unique_programs


class Measurement(db.Model):
    measurement_id = db.Column(db.Integer, primary_key=True)
    measurement_point = db.Column(db.String(50))
    file_name = db.Column(db.String(50))
    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
    column = db.Column(db.String(50))
    x = db.Column(db.Numeric)
    y = db.Column(db.Numeric)
    z = db.Column(db.Numeric)
    nominal = db.Column(db.Numeric)
    lsl = db.Column(db.Numeric)
    usl = db.Column(db.Numeric)
    i = db.Column(db.Numeric)
    j = db.Column(db.Numeric)
    k = db.Column(db.Numeric)
    actual = db.Column(db.Numeric)
    dev = db.Column(db.Numeric)
    program_id = db.Column(db.Integer, db.ForeignKey('program.program_id'))

    def __repr__(self):  # changes output of object when called
        return f"{self.measurement_point}"

    @classmethod
    def read_file(cls, program: dict, program_id: int):
        """
        reads a cmm .res file and extracts data
        into a list of dicts
        :param program: path to file (str)
        :param program_id: parent program_id (int)
        :return:
        """
        measurement_points = []
        file_path = program['path']
        with open(file_path, 'rt') as f:
            reader = csv.reader(f)
            raw_data = list(map(list, reader))
            for idx, item in enumerate(raw_data[32], start=3):
                if idx >= len(raw_data[32]): break
                measurement_points.append({
                    'program_id': program_id,
                    'file_name': raw_data[33][0],
                    'date': raw_data[33][1],
                    'time': raw_data[33][2],
                    'column': raw_data[8][idx],
                    'x': raw_data[9][idx],
                    'y': raw_data[10][idx],
                    'z': raw_data[11][idx],
                    'nominal': raw_data[12][idx],
                    'lsl': raw_data[13][idx],
                    'usl': raw_data[14][idx],
                    'i': raw_data[15][idx],
                    'j': raw_data[16][idx],
                    'k': raw_data[17][idx],
                    'actual': raw_data[33][idx],
                    'dev': round(float(raw_data[33][idx]) - float(raw_data[12][idx]), 3),
                    'measurement_point': raw_data[32][idx],
                })
        return measurement_points
