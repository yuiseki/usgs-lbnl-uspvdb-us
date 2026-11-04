"""Build data/uspvdb_v4_0_20260414.parquet (GeoParquet, EPSG:4326) from the GeoJSON release and cross-check against the Shapefile and CSV."""
import csv, json, sys
import geopandas as gpd, numpy as np, pandas as pd
V = "uspvdb_v4_0_20260414"
g = gpd.read_file(f"work/geojson/{V}.geojson")
s = gpd.read_file(f"work/shp/{V}.shp")
c = pd.read_csv(f"work/csv/{V}.csv", dtype=str, keep_default_na=False)
print("rows geojson/shp/csv:", len(g), len(s), len(c))
assert g.case_id.is_unique and s.case_id.is_unique and c.case_id.is_unique
assert set(g.case_id) == set(s.case_id) == set(c.case_id.astype(int))
for extra in ("FID", "Id"):
    for nm, d in (("geojson", g), ("shp", s)):
        if extra in d.columns: print(extra, nm, "unique values:", d[extra].nunique(), "min/max:", d[extra].min(), d[extra].max())
cols = list(c.columns)
for nm, d in (("geojson", g), ("shp", s)):
    assert [x for x in d.columns if x not in ("geometry", "FID", "Id")] == cols, nm + ": column order differs"
g = g[cols + ["geometry"]]; s = s[cols + ["geometry"]]
gi = g.set_index("case_id").sort_index(); si = s.set_index("case_id").sort_index(); ci = c.assign(case_id=c.case_id.astype(int)).set_index("case_id").sort_index()
bad = {}
for col in cols[1:]:
    a = gi[col]; b = si[col]
    if a.dtype.kind in "fi":
        an = a.astype(float).to_numpy(); bn = b.astype(float).to_numpy(); cn = pd.to_numeric(ci[col].replace("", np.nan)).to_numpy()
        eq_sg = np.isclose(an, bn, rtol=0, atol=1e-6, equal_nan=True); eq_cg = np.isclose(an, cn, rtol=0, atol=1e-4, equal_nan=True)
    else:
        a2 = a.fillna("").astype(str); b2 = b.fillna("").astype(str)
        eq_sg = (a2.values == b2.values); eq_cg = (a2.values == ci[col].values)
    if not eq_sg.all() or not eq_cg.all(): bad[col] = (int((~eq_sg).sum()), int((~eq_cg).sum()))
print("attribute mismatches (shp vs geojson, csv vs geojson):", bad or "none")
# geometry: reproject shapefile to 4326 and compare
s4 = si.to_crs(4326).geometry; g4 = gi.geometry
rel = []
for k in gi.index:
    a, b = g4[k], s4[k]
    rel.append(a.symmetric_difference(b).area / max(a.area, 1e-18))
rel = np.array(rel); print("geometry symdiff/area: max %.3g, p99 %.3g, >1e-6: %d" % (rel.max(), np.percentile(rel, 99), (rel > 1e-6).sum()))
print("geom types:", g.geometry.geom_type.value_counts().to_dict(), "invalid:", int((~g.geometry.is_valid).sum()), "empty:", int(g.geometry.is_empty.sum()))
print("crs:", g.crs)
out = g.sort_values("case_id").reset_index(drop=True)
import os; os.makedirs("data", exist_ok=True)
out.to_parquet(f"data/{V}.parquet", compression="zstd", index=False)
print("written", os.path.getsize(f"data/{V}.parquet"))
