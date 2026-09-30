# [C] golang-nanoauth authentication bypass vulnerability

## Summary
Severity: Critical
Advisory: GHSA-hrm3-3xm6-x33h
CVE: CVE-2020-36569
CWE: CWE-287, CWE-305
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-hrm3-3xm6-x33h
Type: github-advisory

## Affected
- Go: `github.com/nanobox-io/golang-nanoauth` — affected >=0.0.0-20160722212129-ac0cc4484ad4 <0.0.0-20200131131040-063a3fb69896

## Details
Authentication is globally bypassed in github.com/nanobox-io/golang-nanoauth between v0.0.0-20160722212129-ac0cc4484ad4 and v0.0.0-20200131131040-063a3fb69896 if ListenAndServe is called with an empty token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36569
- https://github.com/nanobox-io/golang-nanoauth/pull/5
- https://github.com/nanobox-io/golang-nanoauth/commit/063a3fb69896acf985759f0fe3851f15973993f3
- https://github.com/nanobox-io/golang-nanoauth
- https://pkg.go.dev/vuln/GO-2020-0004
