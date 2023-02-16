# naptan: a python package

Created to quickly and easily get, view, and map NaPTAN data.

The package's functions return the data from the NaPTAN API as a pandas.DataFrame. This allows the data to be easily filtered, queried and manipulated. Once you have the data, you can export the data as a geoJSON, or view it via an interactive map.

```python
"""
Example code to view all the active NaPTAN stops within Leicester and
Leicestershire on a map in the browser.
"""
import naptan

# get data as a dataframe
# 260 is Leicestershire and 269 is Leicester
leics_stops = naptan.get_area_stops(['260', '269'])

# View the stops in the browser on an interactive map.
naptan.view_map(leics_stops)
```

![coalville-example](docs/map-example.PNG)

## Installation

The latest release can be installed with:

```bash
$ pip install naptan
```

## Documentation

All documentation, tutorials, API reference etc can be found at the package's site: https://mullinscr.github.io/naptan/

## License

MIT. See LICENSE.txt.

## NaPTAN dataset

National public transport access nodes (NaPTAN) is a national dataset of all
public transport 'stops' in England, Scotland and Wales. Bus stops form the vast
majority of the dataset; but there is data on tram, metro, tube, rail, ferry and
air services too.

Included in the dataset, along with the unique identifiers, is common name,
locality, stop type, bearing of onward travel, and status (active, inactive or pending).

More information can be found on the UK government's website:

- [NaPTAN guide for data managers](https://www.gov.uk/government/publications/national-public-transport-access-node-schema/naptan-guide-for-data-managers)
- [NPTG and NaPTAN schema guide (2.5) (pdf)](http://naptan.dft.gov.uk/naptan/schema/2.5/doc/NaPTANSchemaGuide-2.5-v0.67.pdf)