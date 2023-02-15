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

The data is returned from these functions as a pandas DataFrame object, with
columns for the stops' attributes (such as ATCO code, name, location, stop type
etc).

Examples
--------

>> naptan.get_all_stops()
>> naptan.get_area_stops(['260', '269'])
>> naptan.get_specific_stops(['1000DOVA8309', '2700LLTA3054']))
"""
from io import BytesIO
import json
import tempfile
from typing import Iterable, Optional, Union
import webbrowser

import folium
from folium.plugins.fast_marker_cluster import FastMarkerCluster
from folium.plugins import Search
import pandas as pd
from pyproj import CRS, Transformer
import requests


_BASE_URL = 'https://naptan.api.dft.gov.uk'
_API_VERSION = 'v1'


class APIError(Exception):
    """Raised for a status code != 200 returned from NaPTAN API"""


def _get_stops(area_codes: str = '', status: Optional[str] = None) -> pd.DataFrame:
    """Process the API request and returned response."""
    response = _process_request(area_codes)
    return _process_response(response, status)

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

def _convert_coords(df: pd.DataFrame) -> pd.DataFrame:
    """Ensures the DataFrame has a full compliment of Latitude and Longitude
    values. Fills this data in by converting the mandatory Easting and Northing
    values.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame of stops created by _process_response

    Returns
    -------
    pd.DataFrame
        DataFrame with complete set of Latitude and Longitude values
    """
    crs_27700 = CRS('EPSG:27700')
    crs_4326 = CRS('EPSG:4326')
    transformer = Transformer.from_crs(crs_27700, crs_4326)
    df['Latitude'], df['Longitude'] = transformer.transform(df['Easting'], df['Northing'])
    return df

def _process_response(response: requests.models.Response, status: Optional[str]) -> pd.DataFrame:
    """
    Process the valid returned API response and return a dataframe.

    Parameters
    ----------
    response : requests.models.Response
        The valid response from the NaPTAN API call.

    status : str, optional
        Return only NaPTAN stops with specific status. Must be one of None,
        'active', 'inactive', or 'pending'.

    Returns
    -------
    DataFrame
        All stops returned from valid response.
    """
    stop_df = pd.read_csv(
        BytesIO(response.content),
        dtype={c: str for c in [1, 2, 6, 21, 22, 23, 24, 25]}
    )

    stop_df = _convert_coords(stop_df)

    if status:
        status = status.lower().strip()
        if status not in ('active', 'inactive', 'pending'):
            raise ValueError("`status` must be one of: 'active', 'inactive', or 'pending'")
        return stop_df.query('Status == @status')
    return stop_df

def _format_stop_areas(stops: Iterable[Union[str, int]]) -> str:
    """
    Takes stops or stop areas and limits them to the first three characters.

    Will also handle area codes that have only been passed in as '89' or 89
    instead of '089', for example.

    Parameters
    ----------
    stops : Iterable[str]
        Iterable of stops or area codes to be processed.

    Returns
    -------
    str
        Formatted area code string for passing to the API request, eg. '260,080'
    """
    stops = [str(stop) for stop in stops]
    areas = sorted(list({stop[:3].rjust(3, '0') for stop in stops}))
    return ','.join(areas)

def get_specific_stops(stops: Iterable[str], status: Optional[str] = None) -> pd.DataFrame:
    """
    Returns a dataframe containing just the specified stops, if present in the
    NaPTAN dataset.

    Parameters
    ----------
    stops : Iterable[str]
        Iterable of the desired stops' ATCO code, as strings. For example:
        ['2500DCL4060', '1100DEA10139', '068000000322']

    status : str, optional
        Return only NaPTAN stops with specific status. Must be one of None,
        'active', 'inactive', or 'pending'.

    Returns
    -------
    DataFrame
        Containing just the specified stops.
    """
    stop_areas = _format_stop_areas(stops)
    returned_stops = _get_stops(stop_areas, status)
    return returned_stops.loc[returned_stops['ATCOCode'].isin(stops)]

def get_area_stops(area_codes: Iterable[Union[str, int]], status: Optional[str] = None) -> pd.DataFrame:
    """Returns a dataframe containing all the stops that share the specified area codes.

    Args:
        area_codes: Iterable of the desired area code. Can be strings or numeric.
        For example: ['250', '110'] or [250, 110]

    status : str, optional
        Return only NaPTAN stops with specific status. Must be one of None,
        'active', 'inactive', or 'pending'.

    Returns
    -------
    DataFrame
        Containing all available stops that share the specified area codes.
    """
    stop_areas = _format_stop_areas(area_codes)
    return _get_stops(stop_areas, status)

def get_all_stops(status: Optional[str] = None) -> pd.DataFrame:
    """
    Returns a dataframe with all the available nationwide NaPTAN stops.

    Parameters
    ----------
    status : str, optional
        Return only NaPTAN stops with specific status. Must be one of None,
        'active', 'inactive', or 'pending'.

    Returns
    -------
    DataFrame
        All available NaPTAN stops.
    """
    return _get_stops(status=status)

def _generate_geojson(df: pd.DataFrame) -> str:
    """Creates a geojson string from a stop dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        Input data frame of stops returned from naptan functions.

    Returns
    -------
    str
        json (geojson) formatted string of the stops and their data.
    """
    stops = []

    for stop in df.itertuples():
        stop_geojson = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [stop.Longitude, stop.Latitude],
                },
                'properties': {k: v for k, v in stop._asdict().items() if k != 'Index'}
        }
        stops.append(stop_geojson)

    geojson_str = {
        'type': 'FeatureCollection',
        'features': stops,
    }

    return json.dumps(geojson_str)

def export_geojson(df: pd.DataFrame, path: str) -> None:
    """Export a dataframe of stops as a .json (geojson) file.

    Parameters
    ----------
    df : pd.DataFrame
        Input data frame of stops returned from naptan functions.
    path : str
        Output path. e.g. '~/path/to/dir/naptan_stops.json'
    """
    geojson = _generate_geojson(df)
    with open(path, 'w') as f:
        f.write(geojson)

def create_map(df: pd.DataFrame, disable_cluster_zoom=17) -> folium.Map:
    """Create a folium.Map displaying the stops.

    Parameters
    ----------
    df : pd.DataFrame
        Input data frame of stops returned from naptan functions.
    disable_cluster_zoom : int, optional
        The zoom level at which point points are no longer clustered on the map,
        by default 17.

    Returns
    -------
    folium.Map
        folium.Map object
    """
    central_point = df['Latitude'].median(), df['Longitude'].median()
    m = folium.Map(location=[*central_point])
    data = [
        [lat, lng, atco, common_name, locality, ind, bearing]
        for lat, lng, atco, common_name, locality, ind, bearing in zip(
            df['Latitude'], df['Longitude'], df['ATCOCode'], df['CommonName'],
            df['LocalityName'], df['Indicator'], df['Bearing']
        )
    ]
    callback = """
        function (row) {
            var marker;
            marker = L.marker(
                new L.LatLng(row[0], row[1]),
                {"Identifier": row[2] + ": " + row[3] + ", " + row[4]}
            );
            marker.bindPopup(
                "<b>" + row[2] + "</b>"
                + "</br>"
                + row[4] + ", " + row[5] + " " + row[3]
                + "</br>"
                + "<a href='https://bustimes.org/stops/" + row[2] + "' target='_blank'>Bus Times (" + row[6] + ")</a>");
            return marker;
        };
    """
    mc = FastMarkerCluster(
        data,
        callback=callback,
        disableClusteringAtZoom=disable_cluster_zoom
    ).add_to(m)
    Search(layer=mc, search_label='Identifier', search_zoom=18, placeholder='Search by ATCO code...').add_to(m)
    return m

def view_map(df: pd.DataFrame, disable_cluster_zoom=17) -> None:
    """View the stops on a folium-generated map, in the browser.

    Parameters
    ----------
    df : pd.DataFrame
        Input data frame of stops returned from naptan functions.
    disable_cluster_zoom : int, optional
        The zoom level at which point points are no longer clustered on the map,
        by default 17.
    """
    m = create_map(df, disable_cluster_zoom)
    f = tempfile.NamedTemporaryFile(mode='wb', delete=False) 
    m.save(f.name + '.html')
    webbrowser.open(f.name + '.html')