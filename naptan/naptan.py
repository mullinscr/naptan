"""
Wrapper for the UK Government's public transport NaPTAN API.

This module provides functionality to extract data from the UK's Department for
Transport NaPTAN API. The national public transport access nodes (NaPTAN) is a
national dataset of all public transport 'stops' in England, Scotland and Wales.
See: https://www.gov.uk/government/publications/national-public-transport-access-node-schema/html-version-of-schema

The public transport stops are available to extract from the API with three
functions:

- `naptan.get_all_stops`
- `naptan.get_area_stops`
- `naptan.get_specific_stops`

The data is returned from these functions as a 'StopList' object, within which are
Stop objects that hold the stop's attributes (such as ATCO code, name, location
stop type etc).

StopList objects can be filtered via stop atco_code, type and status. They can
also be converted to a pandas dataframe or python dictionary. Stop objects can
also be converted to a python dictionary.

Examples
--------

>> stop_list = naptan.get_area_stops(['269'])
>> filtered = stop_list.filter(status=['active'])
>> filtered.to_dict()
>> filtered.to_dataframe()
>> filtered[0].to_dict()

"""
from io import BytesIO
from typing import Iterable

import requests
import pandas as pd


_BASE_URL = 'https://naptan.api.dft.gov.uk'
_API_VERSION = 'v1'


class APIError(Exception):
    """Raised for a status code != 200 returned from NaPTAN API"""


def _get_stops(area_codes: str = '') -> pd.DataFrame:
    """Process the API request and returned response."""
    response = _process_request(area_codes)
    return _process_response(response)

def _process_request(area_codes: str) -> requests.models.Response:
    """
    Processes the API request.

    Parameters
    ----------
    area_codes : str
        The formatted ATCO area codes string. Eg. '269,260,080'.

    Returns
    -------
    requests.models.Response
        The NaPTAN API response.

    Raises
    ------
    APIError
        If the response status code is not 200, then raise error with the status
        code and reason.
    """
    response = requests.get(f'{_BASE_URL}/{_API_VERSION}/access-nodes',
        timeout = 30,
        params = {
            'atcoAreaCodes': area_codes,
            'dataFormat': 'csv'
        }
    )

    if response.status_code != 200:
        raise APIError(response.status_code, response.reason)
    return response

def _process_response(response: requests.models.Response) -> pd.DataFrame:
    """
    Process the valid returned API response and return a dataframe.

    Parameters
    ----------
    response : requests.models.Response
        The valid response from the NaPTAN API call.

    Returns
    -------
    DataFrame
        All stops returned from valid response.
    """
    return pd.read_csv(
        BytesIO(response.content),
        dtype={c: str for c in [1, 2, 6, 21, 22, 23, 24, 25]}
    )

def _format_stop_areas(stops: Iterable[str]) -> str:
    """
    Takes stops or stop area strings and limits them to the first three digits.

    Will also handle area codes that have only been passed in as '89' instead
    of '089', for example.

    Parameters
    ----------
    stops : Iterable[str]
        Iterable of stops or area codes to be processed.

    Returns
    -------
    str
        Formatted area code string for passing to the API request, eg. '260,080'
    """
    areas = sorted(list({stop[:3].rjust(3, '0') for stop in stops}))
    return ','.join(areas)

def get_specific_stops(stops: Iterable[str]) -> pd.DataFrame:
    """
    Returns a dataframe containing just the specified stops, if present in the
    NaPTAN dataset.

    Parameters
    ----------
    stops : Iterable[str]
        Iterable of the desired stops' ATCO code, as strings. For example:
        ['2500DCL4060', '1100DEA10139', '068000000322']

    Returns
    -------
    DataFrame
        Containing just the specified stops.
    """
    stop_areas = _format_stop_areas(stops)
    returned_stops = _get_stops(stop_areas)
    return returned_stops.loc[returned_stops['ATCOCode'].isin(stops)]

def get_area_stops(area_codes: Iterable[str]) -> pd.DataFrame:
    """
    Returns a dataframe containing all the stops that share the specified area codes.

    Parameters
    ----------
    area_codes : Iterable[str]
        Iterable of the desired area codes as strings. For example: ['250', '110']

    Returns
    -------
    DataFrame
        Containing all available stops that share the specified area codes.
    """
    stop_areas = _format_stop_areas(area_codes)
    return _get_stops(stop_areas)

def get_all_stops() -> pd.DataFrame:
    """
    Returns a dataframe with all the available nationwide NaPTAN stops.

    Returns
    -------
    DataFrame
        All available NaPTAN stops.
    """
    return _get_stops()
