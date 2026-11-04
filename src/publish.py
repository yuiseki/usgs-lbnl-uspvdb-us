#!/usr/bin/env python3
"""Push the card, licence, provenance, Parquet, the provider's raw files, docs and scripts to the Hub.

uv run python src/publish.py             # dry run: lists the files and sizes (the default; nothing is sent)
uv run python src/publish.py --push      # one commit; prints the sha and writes docs/revision.json (NOT to be run without the person's approval)

The provider's files may be republished: the provider says its data are free and in the public domain (quoted in LICENSE).
Not published: work/ (unzipped copies), the HTTP header files, caches.
"""
import argparse, hashlib, json, sys
from datetime import UTC, datetime
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REPO = "yuiseki/usgs-lbnl-uspvdb-us"
PQ = "uspvdb_v4_0_20260414.parquet"


def collect() -> dict[str, Path]:
    card = (DATA / "README.md").read_text(encoding="utf-8")
    ver = json.loads((ROOT / "docs" / "verification.json").read_text())
    prof = json.loads((ROOT / "docs" / "profile.json").read_text())
    if "license: other" not in card or "license_name:" not in card:
        raise SystemExit("the card does not declare license: other with a license_name")
    if "Map services and data are available from Large-Scale Solar Photovoltaic Database" not in card:
        raise SystemExit("the card lacks the provider's acknowledgment")
    if ver["csv_vs_geojson_attribute_mismatches"] != 0 or not ver["shp_vs_geojson_attribute_differences_are_only_null_encoding"]:
        raise SystemExit("verification has unexplained attribute differences")
    if not prof["second_route"]["equal"]:
        raise SystemExit("the second route disagrees")
    t = pq.read_table(DATA / "parquet" / PQ)
    if t.num_rows != prof["rows"] or f"{t.num_rows:,}" not in card:
        raise SystemExit("row count differs from the profile or the card")
    if "FID" in t.column_names or "Id" in t.column_names:
        raise SystemExit("GIS artefact columns must be dropped")
    files: dict[str, Path] = {"README.md": DATA / "README.md", "LICENSE": DATA / "LICENSE", "provenance.yaml": DATA / "provenance.yaml", f"parquet/{PQ}": DATA / "parquet" / PQ}  # fmt: skip
    for p in sorted((ROOT / "raw" / "data").glob("*")):
        if p.is_file() and p.suffix != ".headers":
            files[f"raw/data/{p.name}"] = p
    for p in sorted((ROOT / "docs").glob("*.json")):
        if p.name != "revision.json":
            files[f"docs/{p.name}"] = p
    for sub in ("scripts", "src"):
        for p in sorted((ROOT / sub).glob("*")):
            if p.is_file() and p.suffix in (".py", ".sh"):
                files[f"{sub}/{p.name}"] = p
    return files


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--push", action="store_true", help="upload; needs the person's approval")
    a = ap.parse_args()
    files = collect()
    print(f"{a.repo}\n  {len(files)} files, {sum(p.stat().st_size for p in files.values()):,} bytes")
    for k, v in files.items():
        print(f"  {v.stat().st_size:>12,}  {k}")
    if not a.push:
        print("\ndry run. pass --push to upload")
        return 0
    from huggingface_hub import CommitOperationAdd, HfApi

    api = HfApi()
    api.create_repo(a.repo, repo_type="dataset", exist_ok=True, private=False)
    ops = [CommitOperationAdd(path_in_repo=k, path_or_fileobj=str(v)) for k, v in files.items()]
    c = api.create_commit(a.repo, ops, repo_type="dataset", commit_message="Add USPVDB V4.0 (2026-04-14): 6,611 U.S. large-scale PV facilities as GeoParquet, with the provider's files")
    rev = {"repo": a.repo, "revision": c.oid, "pushed": datetime.now(UTC).isoformat(timespec="seconds"), "sha256": {k: sha256(v) for k, v in files.items()}}  # fmt: skip
    (ROOT / "docs" / "revision.json").write_text(json.dumps(rev, indent=1) + "\n")
    print(f"pushed {a.repo} revision {c.oid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
