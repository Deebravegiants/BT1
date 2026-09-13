# [M] Hugo: Symlink confinement bypass in resources.Get

## Summary
Severity: Medium
Advisory: GHSA-fw87-fv5r-9fpw
CVE: CVE-2026-50135
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-fw87-fv5r-9fpw
Type: github-advisory

## Affected
- Go: `github.com/gohugoio/hugo` — affected >=0.123.0 <0.162.0

## Details
**Commit:** [f8b5fa09a6](https://github.com/gohugoio/hugo/commit/f8b5fa09a6) — _Fix prevention of direct symlink reads in resources.Get_
**Affected versions:** v0.123.0 through v0.161.1. Earlier versions are not affected.
**Fixed in:** v0.162.0.
**Severity:** Medium. Requires the attacker to be able to place (or convince a site author to place) a symlink inside a mounted directory — for example, inside a locally-vendored theme under `themes/`. Themes mounted as Go modules from GitHub have symlinks stripped on download and are not affected. Multi-directory walks (e.g. content/asset walking) were not affected either; only direct lookups via `resources.Get` followed symlinks.

**Description.** Hugo's virtual filesystem is designed so that files under a mount cannot reach outside the mount tree. A regression introduced in v0.123.0 caused `RootMappingFs.statRoot` to call `Stat` (which follows symlinks) instead of `Lstat`, so a direct `resources.Get "somefile"` where `somefile` was a symlink pointing outside the mount would return the target's contents. This effectively let a symlink planted inside a theme or local mount read arbitrary files reachable to the user running `hugo`.

**Mitigation.** v0.162.0 calls `LstatIfPossible` and rejects symlinked entries with `os.ErrNotExist`, matching the behaviour of pre-v0.123.0 releases and of the directory-walking code paths.

## References
- https://github.com/gohugoio/hugo/security/advisories/GHSA-fw87-fv5r-9fpw
- https://github.com/gohugoio/hugo/commit/f8b5fa09a64950c32b803821ede411ebfe772b7a
- https://github.com/gohugoio/hugo
- https://github.com/gohugoio/hugo/releases/tag/v0.162.0
