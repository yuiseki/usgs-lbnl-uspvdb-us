# usgs-lbnl-uspvdb-us

The U.S. Large-Scale Solar Photovoltaic Database (USPVDB) V4.0 (2026-04-14) by USGS and LBNL, repackaged as GeoParquet with the provider's files.
The dataset is on the Hugging Face Hub: <https://huggingface.co/datasets/yuiseki/usgs-lbnl-uspvdb-us> (revision `5e4305552ac145b53bb348cc7cc2190013ef358a`, read back and checked against this tree).

- Card, licence, provenance: `data/README.md`, `data/LICENSE`, `data/provenance.yaml` (the Hub's README.md is `data/README.md`).
- Data: `data/parquet/uspvdb_v4_0_20260414.parquet`; the provider's files: `raw/data/`.
- Checks: `docs/verification.json`, `docs/profile.json`, `docs/verify_hub.json`.
- Scripts: `scripts/`, `src/publish.py`.

Source: <https://energy.usgs.gov/uspvdb/> (data free and in the public domain; the provider asks for the acknowledgment in `data/README.md`). Not a publication of USGS or LBNL.
