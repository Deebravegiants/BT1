# [M] Cross-site scripting in bluemonday

## Summary
Severity: Medium
Advisory: GHSA-3x58-xr87-2fcj
CVE: CVE-2021-29272
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-3x58-xr87-2fcj
Type: github-advisory

## Affected
- Go: `github.com/microcosm-cc/bluemonday` — affected >=0 <1.0.5

## Details
bluemonday before 1.0.5 allows XSS because certain Go lowercasing converts an uppercase Cyrillic character, defeating a protection mechanism against the "script" string.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29272
- https://github.com/microcosm-cc/bluemonday/issues/111
- https://github.com/microcosm-cc/bluemonday/commit/524f142fe46e945b7dcd291d7805c4b7dcf75bee
- https://github.com/microcosm-cc/bluemonday
- https://github.com/microcosm-cc/bluemonday/releases/tag/v1.0.5
- https://pkg.go.dev/vuln/GO-2022-0762
- https://vuln.ryotak.me/advisories/4
- https://vuln.ryotak.me/advisories/4.txt
