## [0.2.1](https://github.com/mullinscr/naptan/releases/tag/v0.2.1)

### Added

- Documentation and tutorials etc via this website (https://mullinscr.github.io/naptan/)


## [0.2.0](https://github.com/mullinscr/naptan/releases/tag/v0.2.0)

### Changed

- Re-write of the package to enable ease of working with the returned NaPTAN data (data now returned as a pandas.DataFrame).
-   `get_area_stops` now accepts a mix of numbers and strings

### Added

- `export_geojson`: export the stop data and its attributes as geoJSON file.
- `create_map`: create a folium.Map object displaying the stops and some key attributes.
- `view_map`: create the folium.Map as above, and display it in the browser.
- `naptan.ATCO_CODES`: a package level variable to display the ATCO codes to area lookup table

## [0.1.0](https://github.com/mullinscr/naptan/releases/tag/v0.1.0)

Initial commit. Didn't return stops within a dataframe, or provide the ability
to map them.