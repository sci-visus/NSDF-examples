import os
import re
import math
import datetime

from OpenVisus import *


num_rows = 1749
num_cols = 2049
# variables = {'precipitation': [0],
#              'pressure': [0, 100, 200, 500],
#              'temperature': [2, 30, 40, 60, 80, 100, 200, 300, 500, 1000],
#              'virtual_potential_temperature': [2, 30, 40, 60, 80, 100, 200, 300, 500, 1000],
#              'winddirection': [10, 30, 32, 40, 44, 47, 54, 57, 60, 80, 100, 120, 140, 160, 180, 200, 250, 300, 500, 1000],
#              'windspeed': [10, 30, 32, 40, 44, 47, 54, 57, 60, 80, 100, 120, 140, 160, 180, 200, 250, 300, 500, 1000]}

variables = {'precipitation': [0],
             'pressure': [0, 100, 200, 500],
             'temperature': [2, 30, 60, 100, 200, 300, 500, 1000],
             'virtual_potential_temperature': [2, 30, 60, 100, 200, 300, 500, 1000],
             'winddirection': [10, 30, 60, 100, 200, 300, 500, 1000],
             'windspeed': [10, 30, 60, 100, 200, 300, 500, 1000]}


def create_directory(path):
    if os.path.exists(path):
        print(f'Directory exists: {path}')
    else:
        os.mkdir(path)
        print(f'Directory created: {path}')


def build_variable(variable, elevation):
    return f'{variable}_{elevation}m'


def list_files(directory, extension='.nc'):
    files = os.listdir(directory)

    # Remove any files that are not NetCDF
    files = [file for file in files if file.endswith(extension)]
    files.sort()

    return files


def convert_date_to_time_step(date):
    nums = re.findall(r'\d+', date)

    year = nums[0]
    month = nums[1]
    day = nums[2]
    hour = nums[3]

    start_of_year = datetime.datetime(int(year), 1, 1)
    current_date = datetime.datetime(int(year), int(month), int(day))

    days = (current_date - start_of_year).days

    return days * 24 + int(hour)


def convert_time_step_to_date(year, time_step):
    hour = time_step % 24
    day = math.floor(time_step / 24)

    start_of_year = datetime.datetime(year, 1, 1)

    target_date = start_of_year + datetime.timedelta(days=day)

    return f'{target_date.year}-{target_date.month:02d}-{target_date.day:02d}_{hour:02d}_00_00'


def get_fields():
    fields = [Field('latitude', 'float32'), Field('longitude', 'float32')]

    for variable in variables:
        for elevation in variables[variable]:
            field = Field(build_variable(variable, elevation), 'float32')
            fields.append(field)

    return fields


def get_dims(reverse=False):
    return [num_cols, num_rows] if reverse else [num_rows, num_cols]


def get_ram_access(idx_file):
    ram_access = idx_file.createAccess(StringTree.fromString("<access type='RamAccess' chmod='rw' available='0' compression='raw'/>"))

    assert ram_access.bDisableWriteLocks
    assert ram_access.compression == ''

    return ram_access


def get_disk_access(idx_file):
    disk_access = idx_file.createAccess()

    return disk_access
