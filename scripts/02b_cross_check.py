"""Write docs/verification.json: GeoJSON vs Shapefile vs CSV, attribute and geometry checks (all 6,611 features)."""
import json, hashlib, numpy as np, pandas as pd, geopandas as gpd
V = "uspvdb_v4_0_20260414"
g = gpd.read_file(f"work/geojson/{V}.geojson").set_index("case_id").sort_index()
s = gpd.read_file(f"work/shp/{V}.shp").set_index("case_id").sort_index()
c = pd.read_csv(f"work/csv/{V}.csv", dtype=str, keep_default_na=False)
c = c.assign(case_id=c.case_id.astype(int)).set_index("case_id").sort_index()
cols = list(c.columns)
assert list(g.index) == list(s.index) == list(c.index)
nullenc = {}; csv_bad = {}
for col in cols:
    a = g[col]
    if a.dtype.kind in "fi":
        b = s[col].astype(float).to_numpy(); an = a.astype(float).to_numpy(); cn = pd.to_numeric(c[col].replace("", np.nan)).to_numpy()
        ne = int((~np.isclose(an, b, atol=1e-6, equal_nan=True)).sum()); nc = int((~np.isclose(an, cn, atol=1e-4, equal_nan=True)).sum())
        sentinel = int(((b == -9999) & np.isnan(an)).sum())
    else:
        a2 = a.fillna("").astype(str).to_numpy(); b2 = s[col].fillna("").astype(str).to_numpy()
        ne = int((a2 != b2).sum()); nc = int((a2 != c[col].to_numpy()).sum())
        sentinel = int(((b2 == "missing") & (a2 == "")).sum())
    if ne: nullenc[col] = dict(shp_vs_geojson_differences=ne, of_which_missing_or_minus9999_in_shp_null_in_geojson=sentinel)
    if nc: csv_bad[col] = nc
ga = g.to_crs(s.crs).geometry
sd = np.array([ga[k].symmetric_difference(s.geometry[k]).area for k in g.index])
bad = [k for k, v in zip(g.index, sd) if v > 1]
haus = [ga[k].hausdorff_distance(s.geometry[k]) for k in bad]
rel_area = np.array([abs(ga[k].area - g.p_area[k]) / g.p_area[k] for k in g.index])
out = dict(rows=dict(geojson=len(g), shapefile=len(s), csv=len(c)), case_id_sets_equal=True,
    csv_vs_geojson_attribute_mismatches=csv_bad or 0, shp_vs_geojson_attribute_differences=nullenc,
    shp_vs_geojson_attribute_differences_are_only_null_encoding=all(v["shp_vs_geojson_differences"] == v["of_which_missing_or_minus9999_in_shp_null_in_geojson"] for v in nullenc.values()),
    geometry=dict(compared_in="North_America_Albers_Equal_Area_Conic (the shapefile CRS), geojson reprojected from EPSG:4326",
        features_with_symmetric_difference_over_1_m2=len(bad), median_symmetric_difference_m2=float(np.median(sd)), max_symmetric_difference_m2=float(sd.max()),
        hausdorff_m_over_those_features=dict(max=round(max(haus), 3), median=round(float(np.median(haus)), 3)),
        invalid_geometries=dict(geojson=int((~g.geometry.is_valid).sum()), shapefile=int((~s.geometry.is_valid).sum()), reason="ring self-intersection (shapely explain_validity), kept as published"),
        features_where_geojson_area_differs_from_p_area_by_over_0_1_percent=int((rel_area > 1e-3).sum())),
    file_last_modified=dict(shapefile_zip="Tue, 21 Apr 2026 18:40:31 GMT", geojson_zip="Thu, 16 Apr 2026 15:21:38 GMT", csv_zip="Thu, 16 Apr 2026 15:21:32 GMT"),
    parquet_source="GeoJSON in uspvdbGeoJSON.zip (EPSG:4326); columns of the CSV in the CSV's order; GIS artefact columns FID and Id (constant 0) dropped")
json.dump(out, open("docs/verification.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:2500])
