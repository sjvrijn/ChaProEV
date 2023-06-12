'''
Author: Omar Usmani (Oar.Usmani@TNO.nl)
This module defines time structures.

It contains the following functions:
1. **get_time_range:** This function returns the time range of the run, and the
    associated hour numbers, based on values found in the
    parameters file.
2. **get_time_stamped_dataframe:** This function creates a DataFrame with the
timestamps of the run as index (and hour numbers as a column).
'''


import datetime

import pandas as pd
import numpy as np

import cookbook as cook


def get_time_range(parameters_file_name):
    '''
    This function returns the time range of the run, and the
    associated hour numbers, based on values found in the
    parameters file.
    '''

    parameters = cook.parameters_from_TOML(parameters_file_name)

    run_start_parameters = parameters['run']['start']
    run_start_year = run_start_parameters['year']
    run_start_month = run_start_parameters['month']
    run_start_day = run_start_parameters['day']
    run_start_hour = run_start_parameters['hour']
    run_start_minute = run_start_parameters['minute']

    run_start = datetime.datetime(
        run_start_year, run_start_month, run_start_day,
        run_start_hour, run_start_minute
    )

    run_end_parameters = parameters['run']['end']
    run_end_year = run_end_parameters['year']
    run_end_month = run_end_parameters['month']
    run_end_day = run_end_parameters['day']
    run_end_hour = run_end_parameters['hour']
    run_end_minute = run_end_parameters['minute']

    run_end = datetime.datetime(
        run_end_year, run_end_month, run_end_day,
        run_end_hour, run_end_minute
    )

    run_parameters = parameters['run']
    run_frequency_parameters = run_parameters['frequency']
    run_frequency_size = run_frequency_parameters['size']
    run_frequency_type = run_frequency_parameters['type']
    run_frequency = f'{run_frequency_size}{run_frequency_type}'

    run_range = pd.date_range(
        start=run_start, end=run_end, freq=run_frequency, inclusive='left'
        # We want the start timestamp, but not the end one, so we need
        # to say it is closed left
    )

    time_parameters = parameters['time']
    SECONDS_PER_HOUR = time_parameters['SECONDS_PER_HOUR']
    first_hour_number = time_parameters['first_hour_number']

    run_hour_numbers = [
        first_hour_number
        + int(
            (
                time_stamp-datetime.datetime(time_stamp.year, 1, 1, 0, 0)
            ).total_seconds()/SECONDS_PER_HOUR
        )
        for time_stamp in run_range
    ]

    return run_range, run_hour_numbers


def get_time_stamped_dataframe(parameters_file_name):
    '''
    This function creates a DataFrame with the timestamps of the
    run as index (and hour numbers as a column).
    '''

    parameters = cook.parameters_from_TOML(parameters_file_name)

    run_range, run_hour_numbers = get_time_range(parameters_file_name)
    time_stamped_dataframe = pd.DataFrame(
        run_hour_numbers, columns=['Hour Number'], index=run_range
    )
    time_stamped_dataframe.index.name = 'Timestamp'

    time_stamped_dataframe['SPINE_hour_number'] = (
        [f't{hour_number:04}' for hour_number in run_hour_numbers]
    )

    location_parameters = parameters['locations']
    locations = list(location_parameters.keys())
    time_stamped_dataframe[locations] = np.empty(
        (len(run_range), len(locations)))
    time_stamped_dataframe[locations] = np.nan

    return time_stamped_dataframe


if __name__ == '__main__':

    parameters_file_name = 'scenarios/baseline.toml'
    print(get_time_range(parameters_file_name))
    print(get_time_stamped_dataframe(parameters_file_name))