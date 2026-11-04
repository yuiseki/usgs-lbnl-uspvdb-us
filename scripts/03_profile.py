"""Profile the Parquet with pandas and cross-check the same numbers through DuckDB reading the CSV (second route)."""
import json, duckdb, geopandas as gpd
V = "uspvdb_v4_0_20260414"
g = gpd.read_parquet(f"data/parquet/{V}.parquet")
nn = {c: int(g[c].isna().sum()) for c in g.columns if c != "geometry"}
prof = dict(rows=len(g), states=int(g.p_state.nunique()), state_list=sorted(g.p_state.unique().tolist()),
            year_min=int(g.p_year.min()), year_max=int(g.p_year.max()), img_date_min=int(g.p_img_date.min()), img_date_max=int(g.p_img_date.max()),
            cap_ac_mw_sum=round(float(g.p_cap_ac.sum()), 1), cap_dc_mw_sum=round(float(g.p_cap_dc.sum()), 1), area_m2_sum=int(g.p_area.sum()),
            nulls=nn, multi_poly=g.multi_poly.value_counts().to_dict(), p_type=g.p_type.value_counts(dropna=False).to_dict(),
            p_dig_conf=g.p_dig_conf.value_counts().sort_index().to_dict(), geometry_types=g.geometry.geom_type.value_counts().to_dict(),
            invalid_geometries=int((~g.geometry.is_valid).sum()), bounds=[round(float(x), 6) for x in g.total_bounds])
con = duckdb.connect()
q = con.execute(f"select count(*), count(distinct p_state), min(p_year), max(p_year), round(sum(p_cap_ac),1), round(sum(p_cap_dc),1), sum(p_area) from read_csv('work/csv/{V}.csv', header=true)").fetchone()
mine = (prof["rows"], prof["states"], prof["year_min"], prof["year_max"], prof["cap_ac_mw_sum"], prof["cap_dc_mw_sum"], prof["area_m2_sum"])
print("duckdb(csv):", q); print("pandas(parquet):", mine); assert tuple(q) == mine, "second route disagrees"
prof["second_route"] = {"engine": "duckdb read_csv on the CSV in uspvdbCSV.zip", "values": list(q), "equal": True}
json.dump(prof, open("docs/profile.json", "w"), indent=1, default=str)
print(json.dumps({k: prof[k] for k in ("rows", "states", "year_min", "year_max", "cap_ac_mw_sum", "area_m2_sum", "invalid_geometries", "multi_poly", "p_dig_conf")}))
print({k: v for k, v in nn.items() if v})
