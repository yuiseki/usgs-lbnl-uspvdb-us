#!/bin/bash
# Serial, 5 s apart, honest UA. Files of USPVDB v4.0 (2026-04-14). Run from project root.
set -u
UA='geo-dataset-collector-yuiseki/0.1 (personal research; yui.matsumura@geolonia.com)'
B=https://energy.usgs.gov/uspvdb/assets/data
for f in uspvdbSHP.zip uspvdbGeoJSON.zip uspvdbCSV.zip uspvdb_v4_0_20260414.xml CHANGELOG.txt; do
  curl -sS -m 120 -A "$UA" -D raw/data/$f.headers -o raw/data/$f -w "$f %{http_code} %{size_download}\n" "$B/$f"
  sleep 5
done
