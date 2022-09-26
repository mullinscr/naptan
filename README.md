# NaPTAN

A Python package to quickly and easily get national public transport access node data from the UK's NaPTAN API.

This package lets you extract data from the UK's Department for Transport NaPTAN API.
The national public transport access nodes (NaPTAN) is a [national dataset](https://www.gov.uk/government/publications/national-public-transport-access-node-schema/html-version-of-schema) of all public transport 'stops' in England, Scotland and Wales.


## Installation

The latest release can be [installed from pip](https://pypi.org/project/naptan/#description) with:

```cmd
$ pip install naptan
```

## Usage

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

```python
import naptan

# Get all stops for area 269 (Leicester)
>>> stop_list = naptan.get_area_stops(['269'])
```

```python
# Filter to active bus stops
>>> filtered = stop_list.filter(status=['active'])

# Convert StopList to python dict
>>> filtered.to_dict()
{'269030001': {'atco_code': '269030001',
  'naptan_code': 'lecdapwj',
  'plate_code': '',
  'cleardown_code': '',
  'common_name': 'Gravel Street',
  'common_name_lang': '',
  'short_common_name': '',
  'short_common_name_lang': '',
  'landmark': 'Sleepmasters',
  'landmark_lang': '',
  'street': 'GRAVEL STREET',
  'street_lang': '',
  'crossing': '',
  'crossing_lang': '',
  'indicator': 'Stand BJ',
  'indicator_lang': '',
  'bearing': 'NE',
  'nptg_locality_code': 'E0057189',
  'locality_name': 'Leicester',
  'parent_locality_name': '',
  'grand_parent_locality_name': '',
...
```

```python
# Now convert to a dataframe
>>> df = filtered.to_dataframe()
>>> df.head()
```

```python
# View the first Stop as a python dict
>>> filtered[0].to_dict()
{'administrative_area_code': 27,
 'atco_code': '269030001',
 'bearing': 'NE',
 'bus_stop_type': 'MKD',
 'cleardown_code': '',
 'common_name': 'Gravel Street',
 'common_name_lang': '',
 'creation_datetime': datetime.datetime(2002, 12, 10, 0, 0, tzinfo=datetime.timezone.utc),
 'crossing': '',
 'crossing_lang': '',
 'default_wait_time': '',
 'easting': 458641,
 'grand_parent_locality_name': '',
 'grid_type': 'UKOS',
 'indicator': 'Stand BJ',
 'indicator_lang': '',
 'landmark': 'Sleepmasters',
 'landmark_lang': '',
 'latitude': 52.639022,
 'locality_centre': '0',
 'locality_name': 'Leicester',
 'longitude': -1.134862,
 'modification': 'revise',
 'modification_datetime': datetime.datetime(2020, 11, 5, 15, 24, 15, 417, tzinfo=datetime.timezone.utc),     
 'naptan_code': 'lecdapwj',
 'northing': 304935,
 'notes': '',
 'notes_lang': '',
 'nptg_locality_code': 'E0057189',
 'parent_locality_name': '',
 'plate_code': '',
 'revision_number': 7,
 'short_common_name': '',
 'short_common_name_lang': '',
 'status': 'active',
 'stop_type': 'BCT',
 'street': 'GRAVEL STREET',
 'street_lang': '',
 'suburb': '',
 'suburb_lang': '',
 'timing_status': 'PTP',
 'town': '',
 'town_lang': ''}
```

## License

MIT License. See LICENSE.txt.