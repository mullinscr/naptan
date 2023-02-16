# Installation

The [latest release](https://github.com/mullinscr/naptan/releases/tag/v0.2.0) can be [installed from the pypi repository](https://pypi.org/project/naptan/#description)
with:

```bash
$ pip install naptan
```

## Dependencies

The current dependencies are:

package                                                  | version | for
---------------------------------------------------------|---------|-------------------------------------------------
[typing](https://docs.python.org/3/library/typing.html)  |         | Type hinting (only if python version < 3.5).
[pandas](https://pandas.pydata.org/)                     |         | Reading, manipulating and returning the data.
[requests](https://requests.readthedocs.io/en/latest/)   |         | Fetting the data from the government's API.
[folium](https://github.com/python-visualization/folium) | >=0.9.0 | Generating maps.
[pyproj](https://github.com/pyproj4/pyproj)              | >=2.0.0 | Coordinate conversion as a precursor to mapping.