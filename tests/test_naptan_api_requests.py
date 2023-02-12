from importlib_resources import files
from unittest.mock import Mock

import pytest
import requests

import naptan
from naptan.naptan import APIError

def _read_response():
    good_response_stream = files('tests.data') \
        .joinpath('good-response.csv')
    with open(good_response_stream, 'rb') as f:
        return f.read()


class GoodResponseMock:
    status_code = 200
    reason = 'OK'
    content = _read_response()


class BadResponseMock:
    status_code = 400
    reason = 'Atco area codes or data format are incorrectly formatted'


@pytest.fixture
def good_response(monkeypatch):
    def mock_get(*args, **kwargs):
        return GoodResponseMock()
    monkeypatch.setattr(requests, "get", mock_get)

@pytest.fixture
def bad_response(monkeypatch):
    def mock_get(*args, **kwargs):
        return BadResponseMock()
    monkeypatch.setattr(requests, "get", mock_get)

@pytest.mark.parametrize('input_list', [
        ['2500DCL4060', '1100DEA10139', '068000000322'],
        ['250', '110', '68'],
        ('250', '110', '068'),
        ['250', '110', '68']
    ]
)
def test_format_stop_areas_with_stop_areas(input_list):
    assert naptan.naptan._format_stop_areas(input_list) == '068,110,250'

def test_format_stop_areas_set():
    areas = {'260', '080', '269'}
    sorted_areas = sorted(list(areas))
    assert naptan.naptan._format_stop_areas(sorted_areas) == '080,260,269'

def test_format_stop_areas_empty():
    stops = []
    assert naptan.naptan._format_stop_areas(stops) == ''

def test_format_stop_areas_non_string():
    areas = [260, 80, 269]
    with pytest.raises(TypeError):
        naptan.naptan._format_stop_areas(areas)

@pytest.mark.parametrize('inputs', [
        ['1100DEA10139', '1100DEA10138', '2500DCL4060'],
        ['110', '110', '250']]
)
def test_format_stop_areas_no_duplicates(inputs):
    assert naptan.naptan._format_stop_areas(inputs) == '110,250'

def test_format_stop_areas_type_mix():
    stops = [250010959, '1100EXT10']
    with pytest.raises(TypeError):
        naptan.naptan._format_stop_areas(stops)

def test_good_request(good_response):
    response = naptan.naptan._process_request('')
    assert response.status_code == 200

def test_bad_request(bad_response):
    with pytest.raises(APIError):
        naptan.naptan._process_request('abc')

def test_good_response():
    response = Mock(spec=requests.models.Response)
    response.content = _read_response()
    stop_df = naptan.naptan._process_response(response)
    assert stop_df.shape[0] == 15
    assert stop_df.iloc[0]['ATCOCode'] == '068000000754'
    assert stop_df.iloc[1]['Easting'] == 346553

def test_get_all_stops(good_response):
    stop_df = naptan.naptan.get_all_stops()
    assert stop_df.shape[0] == 15
    assert stop_df.iloc[0]['ATCOCode'] == '068000000754'
    assert stop_df.iloc[1]['Easting'] == 346553

def test_get_area_stops(good_response):
    stop_df = naptan.naptan.get_area_stops(['068', '110', '250'])
    assert stop_df.shape[0] == 15
    assert stop_df.iloc[7]['ATCOCode'] == '1100DEC11184'
    assert stop_df.iloc[8]['CommonName'] == "Bedland's Lane"

def test_get_specific_stops(good_response):
    stops = ['068000000754', '1100EXT10', '250020084']
    stop_df = naptan.naptan.get_specific_stops(stops)
    assert stop_df.shape[0] == 3
    assert stop_df.iloc[0]['ATCOCode'] == '068000000754'

def test_get_specific_stops_stops_not_present(good_response):
    stops = ['2500DCL4060', '1100DEA10139', '068000000322']
    stop_df = naptan.naptan.get_specific_stops(stops)
    assert stop_df.empty
