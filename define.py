'''
Author: Omar Usmani (Omar.Usmani@TNO.nl)
This module defines and declares classes for the different objects
that define the system (the parameters/defintions come from a parameters file),
namely:
1. **Legs:** Legs are point-to-point vehicle movements (i.e. movements where
    the vehicle goes from a start location and ends/stops at an end location).
2. **Vehicles:** Each vehicle type (or subtype) is defined in this class.
3. **Location:** This class defines the locations where the vehicles are
(available charger power, connectivity, latitude, longitude, etc.).
'''

import datetime


import numpy as np
import pandas as pd

import cookbook as cook
import weather


class Leg:
    '''
    This class defines the legs and their properties, from a parameters
    file that contains a list of instances and their properties.
    Legs are point-to-point vehicle movements (i.e. movements where
    the vehicle goes from a start location and ends/stops at an end location).
    '''

    class_name = 'legs'

    def __init__(leg, name, parameters_file_name):
        leg.name = name

        parameters = cook.parameters_from_TOML(parameters_file_name)
        leg_parameters = parameters['legs'][name]
        leg.distance = leg_parameters['distance']
        leg.duration = leg_parameters['duration']
        leg.hour_in_day_factors = leg_parameters['hour_in_day_factors']
        locations = leg_parameters['locations']
        leg.start_location = locations['start']
        leg.end_location = locations['end']
        road_type_parameters = leg_parameters['road_type_mix']
        leg.road_type_mix = {}
        for road_type in road_type_parameters:
            leg.road_type_mix[road_type] = road_type_parameters[road_type]

    @staticmethod
    def electricity_use_kWh(leg, time_stamp, vehicle, parameters_file_name):
        '''
        This function tells us how much electricity a given leg uses.
        This will depend on the distance, the vehicle's base conusmption,
        and correction factors such as the temperature, the mix of road types,
        and the time of the day.
        '''

        parameters = cook.parameters_from_TOML(parameters_file_name)

        road_types = parameters['transport_factors']['road_types']

        weighted_road_factor = sum(
            leg.road_type_mix[road_type]*vehicle.road_factors[road_type]
            for road_type in road_types
        )

        hour_in_day_index = time_stamp.hour

        # This is the display hour (starting and ending at midnight, not the
        # hour in the user's/trip day (named day_start_hour),
        # which can be different)
        hour_in_day_factor = leg.hour_in_day_factors[hour_in_day_index]

        # For the temperature factor, we take an average of the factor at
        # the start and end locations.
        temperature_factor_start_location = (
            weather.get_location_weather_quantity(
                leg.start_location.latitude,
                leg.start_location.longitude,
                time_stamp,
                'Temperature at 2 meters (°C)',
                'Temperature at 2 meters (°C)',
                parameters_file_name
            )
        )
        temperature_factor_end_location = (
            weather.get_location_weather_quantity(
                leg.end_location.latitude,
                leg.end_location.longitude,
                time_stamp,
                'Temperature at 2 meters (°C)',
                'Temperature at 2 meters (°C)',
                parameters_file_name
            )
        )

        temperature_factor_leg = (
            (
                temperature_factor_start_location
                + temperature_factor_end_location
            ) / 2
        )

        electricity_use_kWh = (
            leg.distance
            * vehicle.base_consumption
            * temperature_factor_leg
            * weighted_road_factor
            * hour_in_day_factor
        )

        return electricity_use_kWh


class Vehicle:
    '''
    This class defines the vehicles and their properties, from a parameters
    file that contains a list of instances and their porperties.
    '''

    class_name = 'vehicles'

    def __init__(vehicle,  name, parameters_file_name):
        vehicle.name = name

        parameters = cook.parameters_from_TOML(parameters_file_name)
        vehicle_parameters = parameters['vehicles'][name]
        vehicle.base_consumption = vehicle_parameters['base_consumption']
        vehicle.battery_capacity = vehicle_parameters['battery_capacity']
        vehicle.solar_panel_size_kWp = vehicle_parameters[
            'solar_panel_size_kWp']

        road_factor_parameters = vehicle_parameters['road_factors']
        vehicle.road_factors = {}
        for road_type in road_factor_parameters:
            vehicle.road_factors[road_type] = road_factor_parameters[road_type]


class Location:
    '''
    This class defines the locations where the vehicles are
    and their properties,  from a parameters
    file that contains a list of instances and their properties.
    '''

    class_name = 'locations'

    def __init__(location,  name, parameters_file_name):
        location.name = name

        parameters = cook.parameters_from_TOML(parameters_file_name)
        location_parameters = parameters['locations'][name]
        location.connectivity = location_parameters['connectivity']
        location.charging_power = location_parameters['charging_power']
        location.latitude = location_parameters["latitude"]
        location.longitude = location_parameters["longitude"]