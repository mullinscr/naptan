import requests
from importlib_resources import files
from unittest.mock import Mock

import pytest

import naptan
from naptan.naptan import APIError, Stop, StopList

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
    assert naptan.naptan._format_stop_areas(input_list) == '250,110,068'

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
    stop_list = naptan.naptan._process_response(response)

    assert isinstance(stop_list, StopList)
    assert len(stop_list) == 15
    assert isinstance(stop_list[0], Stop)
    assert stop_list[0].atco_code == '068000000754'
    assert stop_list[1].easting == 346553

def test_get_all_stops(good_response):
    stop_list = naptan.naptan.get_all_stops()
    assert isinstance(stop_list, StopList)
    assert len(stop_list) == 15
    assert isinstance(stop_list[0], Stop)
    assert stop_list[0].atco_code == '068000000754'
    assert stop_list[1].easting == 346553

def test_get_area_stops(good_response):
    stop_list = naptan.naptan.get_area_stops(['068', '110', '250'])
    assert isinstance(stop_list, StopList)
    assert len(stop_list) == 15
    assert isinstance(stop_list[0], Stop)
    assert stop_list[7].atco_code == '1100DEC11184'
    assert stop_list[8].common_name == "Bedland's Lane"

def test_stoplist_filter_single_stop(good_response):
    stops = ['068000000754']
    stop_list = naptan.naptan.get_all_stops()
    filtered = stop_list.filter(stops=stops)
    assert len(filtered) == 1
    assert filtered[0].atco_code == '068000000754'

def test_stoplist_filter_multiple_stops(good_response):
    stops = ['068000000754', '1100EXT10']
    stop_list = naptan.naptan.get_all_stops()
    filtered = stop_list.filter(stops=stops)
    assert len(filtered) == 2
    assert filtered[0].atco_code == '068000000754'

def test_stoplist_filter_single_stop_type(good_response):
    stop_type = ['AIR']
    stop_list = naptan.naptan.get_all_stops()
    filtered = stop_list.filter(stop_type=stop_type)
    assert len(filtered) == 1
    assert filtered[0].atco_code == '1100EXT10'

def test_stoplist_filter_status(good_response):
    status = ['inactive', 'pending']
    stop_list = naptan.naptan.get_all_stops()
    filtered = stop_list.filter(status=status)
    assert len(filtered) == 2

def test_stoplist_filter_multiple_filter(good_response):
    stop_type = ['BCT']
    status = ['inactive']
    stop_list = naptan.naptan.get_all_stops()
    filtered = stop_list.filter(stop_type=stop_type, status=status)
    assert len(filtered) == 1
    assert filtered[0].atco_code == '068000000115'

def test_stoplist_filter_empty(good_response):
    stop_list = naptan.naptan.get_all_stops()
    filtered = stop_list.filter()
    assert len(filtered) == 15

def test_stoplist_filter_none_returned_from_invalid_filter(good_response):
    stop_list = naptan.naptan.get_all_stops()
    filtered = stop_list.filter(stops=['123456'])
    assert not filtered

def test_stoplist_filter_none_returned_from_invalid_multiple_filter(good_response):
    stop_list = naptan.naptan.get_all_stops()
    filtered = stop_list.filter(stops=['123456'], status=['invalid_status'])
    assert not filtered

def test_get_specific_stops(good_response):
    stops = ['068000000754', '1100EXT10', '250020084']
    stop_list = naptan.naptan.get_specific_stops(stops)
    assert isinstance(stop_list, StopList)
    assert len(stop_list) == 3
    assert isinstance(stop_list[0], Stop)
    assert stop_list[0].atco_code == '068000000754'

def test_get_specific_stops_stops_not_present(good_response):
    stops = ['2500DCL4060', '1100DEA10139', '068000000322']
    stop_list = naptan.naptan.get_specific_stops(stops)
    assert not stop_list

def test_stoplist_to_dict(good_response):
    stops = ['068000000754', '1100EXT10', '250020084']
    stop_list = naptan.naptan.get_specific_stops(stops)
    stop_dict = stop_list.to_dict()

    assert len(stop_dict) == 3
    assert stop_dict.get('250020084') is not None
    stop = stop_dict.get('250020084')
    assert isinstance(stop, dict)
    assert stop.get('longitude') == -2.771641721
    assert stop.get('naptan_code') == 'lanatpap'

def test_stoplist_to_dataframe(good_response):
    stops = ['068000000754', '1100EXT10', '250020084']
    stop_list = naptan.naptan.get_specific_stops(stops)
    df = stop_list.to_dataframe()

    assert df.shape == (3, 43)
    assert df.iloc[0]['atco_code'] == '068000000754'
