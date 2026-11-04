---
license: other
license_name: usgs-public-domain
license_link: https://energy.usgs.gov/uspvdb/
language:
- en
tags:
- united-states
- solar
- photovoltaic
- energy
- facilities
- usgs
- geoparquet
size_categories:
- 1K<n<10K
pretty_name: U.S. Large-Scale Solar Photovoltaic Database (USPVDB) v4.0, April 2026
configs:
- config_name: default
  data_files: parquet/uspvdb_v4_0_20260414.parquet
---

# usgs-lbnl-uspvdb-us

The U.S. Large-Scale Solar Photovoltaic Database (USPVDB), release V4.0 of 2026-04-14 (`USPVDB_V4_0_20260414`):
the locations and array boundaries of 6,611 U.S. photovoltaic facilities of 1 MW or more (50 jurisdictions: 49 states and the District of Columbia),
made by the U.S. Geological Survey (USGS) and the Lawrence Berkeley National Laboratory (LBNL).
The table is the provider's release in one GeoParquet file; values are as published.

Credit (the provider asks for this acknowledgment): "Map services and data are available from Large-Scale Solar Photovoltaic Database, provided by the U.S. Geological Survey and Lawrence Berkeley National Laboratory via https://energy.usgs.gov/uspvdb".
Suggested citation: Fujita, K.S., Ancona, Z.H., Kramer, L.A., Straka, M., Gautreau, T.E., Garrity, C.P., Robson, D., Diffendorfer, J.E., and Hoen, B., 2023, United States Large-Scale Solar Photovoltaic Database (v4.0, April, 2026): U.S. Geological Survey and Lawrence Berkeley National Laboratory data release, <https://doi.org/10.5066/P9IA3TUS>.
Processed. Repackaged by yuiseki from the GeoJSON of the release into GeoParquet; nothing was corrected, filled in, re-projected or merged (see Differences from the provider's files). This is not a publication of USGS or LBNL.

## Licence

The provider's page says: "Map services and data downloaded from the U.S. Large-Scale Solar Photovoltaic Database are free and in the public domain. There are no restrictions; however, we request that the following acknowledgment statement be included in products and data derived from our map services when citing, copying, or reprinting" (the statement is the credit above).
USGS's copyright page says USGS-authored or produced data are in the U.S. Public Domain, and that some non-USGS material on its sites is not.
The attributes come partly from EIA Form 860 (a U.S. government source) and, for `p_type`, mostly from the U.S. EPA's RE-Powering Matrix; the provider does not state a separate licence for them.
The metadata disclaims any warranty. This card sets `license: other` and quotes the provider, because the Hub has no identifier for this wording. See `LICENSE`.

## Files

| path | what |
|---|---|
| `parquet/uspvdb_v4_0_20260414.parquet` | 6,611 rows, one per facility; GeoParquet, geometry in EPSG:4326 (Polygon 3,529, MultiPolygon 3,082) |
| `raw/data/` | the provider's files as downloaded: `uspvdbSHP.zip`, `uspvdbGeoJSON.zip`, `uspvdbCSV.zip`, the FGDC metadata XML, `CHANGELOG.txt`, `MANIFEST.json` (URL, bytes, sha256, Last-Modified) |
| `docs/` | `profile.json`, `verification.json`, `revision.json` |
| `scripts/`, `src/` | fetch, build, cross-check, card, publish and Hub read-back scripts |

## Columns

Same names and order as the provider's CSV. Definitions are in the provider's metadata (`raw/data/uspvdb_v4_0_20260414.xml`); the short form:
`case_id` stable id; `multi_poly` single or multi-part polygon; `eia_id` EIA Form 860 plant code; `p_state`, `p_county`; `ylat`, `xlong` representative point (NAD83);
`p_area` array area in m² (Albers Equal Area); `p_img_date` yyyymmdd of the aerial image used (Maxar); `p_dig_conf` confidence 1 (low) to 4 (high) (counts {'1': 39, '2': 216, '3': 92, '4': 6264});
`p_name`, `p_year` (year of first operation, 1985 to 2025), `p_pwr_reg`, `p_tech_pri`, `p_tech_sec`, `p_sys_type`, `p_axis`, `p_azimuth`, `p_tilt`, `p_battery`, `p_cap_ac`, `p_cap_dc` (MW), `p_type`, `p_agrivolt`, `p_comm` mostly from EIA Form 860;
`p_zscore` z-score of the DC capacity to area ratio (high or low values may be errors).
`geometry` is the array boundary. Totals: 131,573.5 MW AC, 162,802.2 MW DC, 2,852,104,403 m² of arrays.

Empty values are real nulls here (counts: {'p_pwr_reg': 16, 'p_tech_sec': 236, 'p_axis': 284, 'p_azimuth': 222, 'p_tilt': 1323, 'p_battery': 6236, 'p_comm': 5510}).

## Differences from the provider's files

- The GeoJSON, the CSV and the Shapefile hold the same 6,611 facilities (same `case_id`s). The CSV and the GeoJSON agree on every attribute.
  The Shapefile writes a missing value as the string `missing` or the number `-9999`, as the provider's metadata says; the GeoJSON and the CSV use null or blank. Those are the only attribute differences (p_pwr_reg, p_tech_sec, p_axis, p_azimuth, p_tilt, p_battery, p_comm).
- Geometry: 33 features differ between the Shapefile and the GeoJSON by more than 1 m² of symmetric difference (Hausdorff distance at most 0.74 m); the rest are identical to numerical precision. The Shapefile zip is dated 2026-04-21, the other two 2026-04-16 (Last-Modified); the reason for the sub-metre differences is not known.
- 10 geometries are invalid (ring self-intersection) in both formats and were kept as published.
- The GIS columns `FID` and `Id` (not in the CSV; `Id` is 0 everywhere) were dropped.
- A second route checked the counts, the number of states, the year range and the capacity and area sums by DuckDB on the CSV (equal to the Parquet). Details in `docs/verification.json`.

## Cautions

- Footprints and attributes describe facilities up to the fourth quarter of 2025; releases lag installations by more than a year. Some attributes were missing in the source data, and some facilities may be unbuilt, not built at all or elsewhere (the provider's metadata).
- `p_dig_conf` below 4 means the polygon may cover only part of a facility or several records; `p_zscore` flags possible capacity or area errors.
- Rooftop and canopy systems are included (see `p_sys_type`); the database is not only ground-mounted arrays.

## Reproducing

`scripts/01_fetch.sh` downloads the provider's files (serial, honest User-Agent); `scripts/02_build_verify.py`, `02b_cross_check.py`, `03_profile.py` build and check; `scripts/04_card.py` writes this card.
Releases are yearly (V1.0 2023-11-08, V2.0 2024-08-07, V3.0 2025-04-30, V4.0 2026-04-14); this repository follows the latest release.
