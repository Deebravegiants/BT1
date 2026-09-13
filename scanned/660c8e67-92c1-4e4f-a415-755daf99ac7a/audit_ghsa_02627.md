# [C] Tarslip in go-unarr

## Summary
Severity: Critical
Advisory: GHSA-v9j4-cp63-qv62
CVE: CVE-2021-38197
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-v9j4-cp63-qv62
Type: github-advisory

## Affected
- Go: `github.com/gen2brain/go-unarr` — affected >=0 <0.1.4

## Details
unarr.go in go-unarr (aka Go bindings for unarr) 0.1.1 allows Directory Traversal via ../ in a pathname within a TAR archive.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38197
- https://github.com/gen2brain/go-unarr/issues/21
- https://github.com/gen2brain/go-unarr/commit/239ec404d348280b50bbf671327709e8857fc5f4
- https://github.com/gen2brain/go-unarr/releases/tag/v0.1.4
- github.com/gen2brain/go-unarr
