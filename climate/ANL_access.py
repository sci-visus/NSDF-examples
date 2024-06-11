import datetime
import re
import OpenVisus as ov
import numpy as np


def get_date_from_timestep(year: int, timestep: int) -> (int, int, int, int):
    hour = timestep % 24
    day = timestep // 24

    start_of_year = datetime.datetime(year, 1, 1)
    date = start_of_year + datetime.timedelta(days=day)

    return date.year, date.month, date.day, hour


def get_timestep_from_date(date: str | datetime.datetime) -> (int, int):
    # If date is a string, split it into the year, month, day, and hour
    if isinstance(date, str):
        nums = re.findall(r'\d+', date)

        year = int(nums[0])
        month = int(nums[1])
        day = int(nums[2])
        hour = int(nums[3])

        date = datetime.datetime(year=year, month=month, day=day, hour=hour)

    start_of_year = datetime.datetime(year=date.year, month=1, day=1)
    days = (date - start_of_year).days

    return date.year, days * 24 + date.hour


def get_field(date: str | datetime.datetime, field: str, quality: int = 0) -> np.ndarray:
    year, timestep = get_timestep_from_date(date)

    # Cache dataset if it's not currently loaded
    if get_field.current_year != year:
        get_field.current_year = year
        get_field.current_dataset = ov.LoadDataset(f'http://atlantis.sci.utah.edu/mod_visus?dataset=ANL_cstm_d01_{year}&cached=1')

    # Read the data
    return get_field.current_dataset.read(time=timestep, field=field, quality=quality)


# Used to store the dataset that's currently loaded
get_field.current_year = 0
get_field.current_dataset = None
