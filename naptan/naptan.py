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

The data is returned from these functions as a StopList object, within which are
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
import csv
import datetime
import re
import requests
from typing import Any, List, Dict, Optional, Iterable

from attrs import define, field, asdict
import pandas as pd

_BASE_URL = 'https://naptan.api.dft.gov.uk'
_API_VERSION = 'v1'

class APIError(Exception):
    """Raised for a status code != 200 returned from NaPTAN API"""
    pass


def _str_to_datetime(d_str: str) -> Optional[datetime.datetime]:
    """
    Converts a string representation of a datetime into a timezone aware
    datetime.datetime obj.

    Attempts to convert string conforming to ISO 8601 standard.

    Parameters
    ----------
    str : str
        The string to be converted to a datetime.datetime obj.

    Returns
    -------
    datetime.datetime or None
        Return a timezone-aware datetime.datetime obj if the conversion was
        successful, otherwise None.
    """
    if not d_str or not isinstance(d_str, str):
        return None

    # checks for USO 8601 standard, but can't determine if date is valid
    matcher = re.match(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.?(\d{1,6})?\d*([+-]\d.*)?', d_str)
    if not matcher:
        return None
    
    year, month, day, hour, minute, second, microseconds, offset = matcher.groups()
    if not microseconds:
        microseconds = 0

    if offset:
        matcher = re.match(r'([+-])(\d{2}):?(\d{2}):?(\d{2})?', offset)
        sign, hours, minutes, seconds = matcher.groups()
        if not seconds:
            seconds = 0
        if not minutes:
            minutes = 0

        offset_seconds = int(seconds) + (int(minutes) * 60) + (int(hours) * 3600)
        if sign == '-':
            offset_seconds *= -1
        tzinfo=datetime.timezone(datetime.timedelta(seconds=offset_seconds))
    else:
        tzinfo=datetime.timezone(datetime.timedelta(seconds=+0))

    try:
        converted_datetime = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), int(microseconds), tzinfo=tzinfo)
    except ValueError: # the string matched the ISO 8601 standard but wasn't a valid date
        return None
    return converted_datetime

@define
class Stop:
    atco_code: str
    naptan_code: str
    plate_code: str
    cleardown_code: str
    common_name: str
    common_name_lang: str
    short_common_name: str
    short_common_name_lang: str
    landmark: str
    landmark_lang: str
    street: str
    street_lang: str
    crossing: str
    crossing_lang: str
    indicator: str
    indicator_lang: str
    bearing: str
    nptg_locality_code: str
    locality_name: str
    parent_locality_name: str
    grand_parent_locality_name: str
    town: str
    town_lang: str
    suburb: str
    suburb_lang: str
    locality_centre: str
    grid_type: str
    easting: int = field(converter=int)
    northing: int = field(converter=int)
    longitude: float = field(converter=lambda x: float(x) if x else None)
    latitude: float = field(converter=lambda x: float(x) if x else None)
    stop_type: str
    bus_stop_type: str
    timing_status: str
    default_wait_time: str
    notes: str
    notes_lang: str
    administrative_area_code: int = field(converter=int)
    creation_datetime: datetime.datetime = field(converter=lambda x: _str_to_datetime(x))
    modification_datetime: datetime.datetime = field(converter=lambda x: _str_to_datetime(x))
    revision_number: int = field(converter=lambda x: int(x) if x else None)
    modification: str
    status: str

    def to_dict(self) -> Dict[str, Any]:
        """Returns the Stop as a python dictionary, with attributes as keys and
        the attribute values as values."""
        return asdict(self)


@define
class StopList:
    """
    Holds a list of Stop objects.
    """
    _stops: List[Stop]

    def __iter__(self):
        return iter(self._stops)

    def __getitem__(self, n):
        return self._stops[n]

    def __len__(self):
        return len(self._stops)

    def to_dict(self) -> Dict[str, Dict]:
        """
        Returns the StopList data as a dictionary with each Stop object's ATCO
        code as the key.

        Returns
        -------
        Dict[str, Dict]
            The converted StopList.
        """
        return {stop.atco_code: asdict(stop) for stop in self}
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Returns the StopList as a pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            The converted StopList.
        """
        return pd.DataFrame([asdict(stop) for stop in self])

    def filter(
            self,
            stops: Optional[Iterable[str]] = None,
            stop_type: Optional[Iterable[str]] = None,
            status: Optional[Iterable[str]] = None
        ) -> "StopList":
        """
        Returns a new StopList filtered via the `stops`, `stop_type` and `status`
        keywords.

        Parameters
        ----------
        stops : List[str], optional
            List of stop ATCO codes as strings, by default None.
            For example: ['1100DEB11527', '068000000757']
        stop_type : List[str], optional
            List of valid stop types as strings, by default None.
            For example: ['BCT', 'AIR']
        status : List[str], optional
            List of valid stop status types as strings, by default None.
            For example: ['active']

        Returns
        -------
        StopList
            The filtered StopList.
            
        """
        stop_list = self
        if stops:
            stop_list = StopList([stop for stop in stop_list if stop.atco_code in stops])
        if stop_type:
            stop_list = StopList([stop for stop in stop_list if stop.stop_type in stop_type])
        if status:
            stop_list = StopList([stop for stop in stop_list if stop.status in status])
        
        return stop_list


def _get_stops(area_codes: str = '') -> StopList:
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
        params = {
            'atcoAreaCodes': area_codes,
            'dataFormat': 'csv'
        }
    )

    if response.status_code != 200:
        raise APIError(response.status_code, response.reason)
    return response

def _process_response(response: requests.models.Response) -> StopList:
    """
    Process the valid returned API response and return a StopList object.

    Parameters
    ----------
    response : requests.models.Response
        The valid response from the NaPTAN API call.

    Returns
    -------
    StopList
        All stops returned from valid response.
    """
    csv_data = response.content.decode('utf-8').splitlines()
    reader = csv.reader(csv_data[1:])
    return StopList([Stop(*r) for r in reader])

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
    areas = [stop[:3].rjust(3, '0') for stop in stops]
    return ','.join(areas)

def get_specific_stops(stops: Iterable[str]) -> StopList:
    """
    Returns a StopList containing just the specified stops, if present in the
    NaPTAN dataset.

    Parameters
    ----------
    stops : Iterable[str]
        Iterable of the desired stops' ATCO code, as strings. For example:
        ['2500DCL4060', '1100DEA10139', '068000000322']

    Returns
    -------
    StopList
        Containing just the specified stops.
    """
    stop_areas = _format_stop_areas(stops)
    returned_stops = _get_stops(stop_areas)
    return returned_stops.filter(stops=stops)

def get_area_stops(area_codes: Iterable[str]) -> StopList:
    """
    Returns a StopList containing all the stops that share the specified area codes.

    Parameters
    ----------
    area_codes : Iterable[str]
        Iterable of the desired area codes as strings. For example: ['250', '110']

    Returns
    -------
    StopList
        Containing all available stops that share the specified area codes.
    """
    stop_areas = _format_stop_areas(area_codes)
    return _get_stops(stop_areas)

def get_all_stops() -> StopList:
    """
    Returns a StopList with all the available nationwide NaPTAN stops.

    Returns
    -------
    StopList
        All available NaPTAN stops.
    """
    return _get_stops()
