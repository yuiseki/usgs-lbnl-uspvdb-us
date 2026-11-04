#!/usr/bin/env python3
"""AFTER publication only: read the repository back from the Hub at the recorded revision, compare checksums of every file,
the Parquet schema and cells with the local copy, and re-count rows by DuckDB reading the Hub Parquet (second route).
Not run before publication."""
import json, sys
from pathlib import Path

import duckdb, pyarrow.parquet as pq
from huggingface_hub import HfApi, hf_hub_download

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "src"))
from publish import PQ, collect, sha256


def main() -> int:
    rev = json.loads((ROOT / "docs" / "revision.json").read_text())
    repo, sha = rev["repo"], rev["revision"]
    cache = ROOT / "hub_readback"
    local = collect()
    listed = set(HfApi().list_repo_files(repo, repo_type="dataset", revision=sha))
    bad = [f"not on the Hub: {k}" for k in rev["sha256"] if k not in listed]
    for name, want in rev["sha256"].items():
        p = Path(hf_hub_download(repo, name, repo_type="dataset", revision=sha, local_dir=cache))
        if sha256(p) != want:
            bad.append(f"checksum {name}")
        if name in local and name != "docs/revision.json" and sha256(local[name]) != want:
            bad.append(f"local copy changed since the push: {name}")
    hub, mine = pq.read_table(cache / "parquet" / PQ), pq.read_table(local[f"parquet/{PQ}"])
    if not hub.schema.equals(mine.schema, check_metadata=True):
        bad.append("schema")
    if not hub.equals(mine):
        bad.append("cells")
    n = duckdb.connect().execute(f"select count(*), count(distinct case_id), round(sum(p_cap_ac),1) from read_parquet('{cache / 'parquet' / PQ}')").fetchone()
    prof = json.loads((ROOT / "docs" / "profile.json").read_text())
    if tuple(n) != (prof["rows"], prof["rows"], prof["cap_ac_mw_sum"]):
        bad.append(f"duckdb second route: {n}")
    out = {"repo": repo, "revision": sha, "files_checked": len(rev["sha256"]), "files_on_hub": len(listed), "rows": hub.num_rows, "duckdb": list(n), "problems": bad}
    (ROOT / "docs" / "verify_hub.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(bad) if bad else f"OK: the repository at {sha} equals the local copy")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
