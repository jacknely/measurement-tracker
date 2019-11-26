import os
from os.path import basename
import time
import datetime


def get_file_meta_from_directory(directory: str) -> list:
    """
    extracts file details from a directory and returns a list
    :param directory: path of directory in str
    :return: list of dictionary's that contains details
    of all ".ACTL" files in directory
    """
    file_list = []  # creates empty file list
    directory_name = basename(os.path.dirname(directory))  # gets directory name - usually common with cmm program
    for file in os.listdir(directory):
        if file.endswith(".ACTL"):  # filters for .ACTL file extension
            path = directory + "\\" + file  # get file path
            a = os.stat(os.path.join(directory, file))  # assign file metadata to tuple
            file_list.append({
                'file_name': file,
                'date': datetime.datetime.strptime(time.ctime(a.st_ctime), "%a %b %d %H:%M:%S %Y"),
                'program': directory_name,
                'path': path
            })  # [file, created, directory, path]
    return file_list


def sort_program_meta_from_db(db_query):
    """
    changes the format of data pulled from db
    to a list of dicts
    :param db_query: list of sets
    :return: list of dicts that contains details
    of all records in db
    """
    file_list = []
    for index, program in enumerate(db_query):
        file_list.append({
            'file_name': db_query[index].file_name,
            'date': db_query[index].date,
            'program': db_query[index].program,
            'path': db_query[index].path
        })  # [file, created, directory, path]
    return file_list


if __name__ == '__main__':
    pass
