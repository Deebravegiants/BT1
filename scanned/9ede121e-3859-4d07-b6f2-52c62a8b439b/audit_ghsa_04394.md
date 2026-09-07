# [M] Hugo: Symlink confinement bypass in os.ReadFile

## Summary
Severity: Medium
Advisory: GHSA-c3wq-j5vh-68rc
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-c3wq-j5vh-68rc
Type: github-advisory

## Affected
- Go: `github.com/gohugoio/hugo` — affected >=0.123.0 <0.163.1

## Details
**Affected versions:** v0.123.0 through v0.163.0. Earlier versions are not affected.
**Fixed in:** v0.163.1.
**Severity:** Medium. Requires the attacker to be able to place (or convince a site author to place) a symlink inside a mounted directory — for example, inside a locally-vendored theme under `themes/`. Themes mounted as Go modules from GitHub have symlinks stripped on download and are not affected. Multi-directory walks (e.g. content/asset walking) were not affected either; only direct lookups via `resources.Get` followed symlinks.

**Description.** Hugo's virtual filesystem is designed so that files under a mount cannot reach outside the mount tree. A regression introduced in v0.123.0 caused `RootMappingFs.statRoot` to call `Stat` (which follows symlinks) instead of `Lstat`, so a direct `os.ReadFile "somefile"` where `somefile` was a symlink pointing outside the mount would return the target's contents. This effectively let a symlink planted inside a theme or local mount read arbitrary files reachable to the user running `hugo`.

## References
- https://github.com/gohugoio/hugo/security/advisories/GHSA-c3wq-j5vh-68rc
- https://github.com/gohugoio/hugo
