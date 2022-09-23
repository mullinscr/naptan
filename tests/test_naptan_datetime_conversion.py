import datetime

import pytest

import naptan

@pytest.mark.parametrize('input', ['', 'abcd', '123', 123, 0.156])
def test_datetime_conversion_invalid_or_empty_string(input):
    assert naptan.naptan._str_to_datetime(input) is None

@pytest.mark.parametrize('input',
    [
    '0001-17-99T15:30:45',
    '2022-12-01T99:30:45',
    '2000-17-06T23:30:45',
    '1995-10-99T15:30:75',
    '2022-10-01T15:86:45'
    ]
)
def test_datetime_conversion_valid_format_but_invalid_date(input):
    assert naptan.naptan._str_to_datetime(input) is None

@pytest.mark.parametrize('input,valid_date',
    [
        ('2022-03-21T15:30:45', datetime.datetime(2022, 3, 21, 15, 30, 45, tzinfo=datetime.timezone.utc)),
        ('2022-03-21T15:30:45.123', datetime.datetime(2022, 3, 21, 15, 30, 45, 123, tzinfo=datetime.timezone.utc)),
        ('2022-03-21T15:30:45.123456', datetime.datetime(2022, 3, 21, 15, 30, 45, 123456, tzinfo=datetime.timezone.utc)),
        ('2022-03-21T15:30:45.123456789', datetime.datetime(2022, 3, 21, 15, 30, 45, 123456, tzinfo=datetime.timezone.utc)),
        ('2022-03-21T15:30:45+01:00', datetime.datetime(2022, 3, 21, 15, 30, 45, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600)))),
        ('2022-03-21T15:30:45-01:00', datetime.datetime(2022, 3, 21, 15, 30, 45, tzinfo=datetime.timezone(datetime.timedelta(seconds=-3600)))),
        ('2022-03-21T15:30:45+01:30', datetime.datetime(2022, 3, 21, 15, 30, 45, tzinfo=datetime.timezone(datetime.timedelta(seconds=+5400)))),
        ('2022-03-21T15:30:45.123456+01:00', datetime.datetime(2022, 3, 21, 15, 30, 45, 123456, tzinfo=datetime.timezone(datetime.timedelta(seconds=+3600)))),
        ('2022-03-21T15:30:45.123456+0100', datetime.datetime(2022, 3, 21, 15, 30, 45, 123456, tzinfo=datetime.timezone(datetime.timedelta(seconds=+3600))))
    ]
)
def test_datetime_conversion_valid_date(input, valid_date):
    assert naptan.naptan._str_to_datetime(input) == valid_date