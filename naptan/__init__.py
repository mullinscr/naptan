from .naptan import get_specific_stops, get_area_stops, get_all_stops

def read_atco_lookup():
    """Read the markdown file containing the atco_code lookups, returning as a
    pandas DataFrame."""
    import io
    import pandas as pd
    import pkgutil

    data = pkgutil.get_data(__package__, 'atco_code_and_areas.md')
    if not data:
        raise FileNotFoundError('`atco_code_and_areas.md` could not be located.')

    atco_df = pd.read_table(
        io.BytesIO(data),
        sep='|',
        header=0,
        skipinitialspace=True,
        dtype=str
    ).iloc[1:]

    # to remove whitespace from markdown
    atco_df.columns = atco_df.columns.str.strip()
    for col in atco_df.columns:
        atco_df[col] = atco_df[col].str.strip()
    return atco_df

ATCO_CODES_LOOKUP = read_atco_lookup()

__version__ = '0.1.0'
__author__ = 'Callum Mullins'