from .naptan import get_specific_stops, get_area_stops, get_all_stops, export_geojson, view_map, create_map

def read_atco_lookup():
    """Read the markdown file containing the atco_code lookups, returning as a
    pandas DataFrame."""
    import io
    import pandas as pd
    import pkgutil

    data = pkgutil.get_data(__package__, 'atco_codes.csv')
    if not data:
        raise FileNotFoundError('`atco_codes.csv` could not be located.')

    return pd.read_csv(io.BytesIO(data))

ATCO_CODES = read_atco_lookup()

__version__ = '0.2.0'
__author__ = 'Callum Mullins'