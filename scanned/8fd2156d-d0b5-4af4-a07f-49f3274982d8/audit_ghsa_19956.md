# [H] nosurf vulnerable to improper input validation

## Summary
Severity: High
Advisory: GHSA-5x84-q523-vvwr
CVE: CVE-2020-36564
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-5x84-q523-vvwr
Type: github-advisory

## Affected
- Go: `github.com/justinas/nosurf` — affected >=0 <1.1.1

## Details
Due to improper validation of caller input, validation is silently disabled if the provided expected token is malformed, causing any user supplied token to be considered valid.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36564
- https://github.com/justinas/nosurf/pull/60
- https://github.com/justinas/nosurf/commit/4d86df7a4affa1fa50ab39fb09aac56c3ce9c314
- https://github.com/justinas/nosurf
- https://pkg.go.dev/vuln/GO-2020-0049
