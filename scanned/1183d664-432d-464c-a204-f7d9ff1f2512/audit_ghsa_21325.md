# [H] goxmldsig vulnerable to crash on nil-pointer dereference caused by sending malformed XML signatures

## Summary
Severity: High
Advisory: GHSA-mqqv-chpx-vq25
CVE: CVE-2020-7711
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-07
Source: https://github.com/advisories/GHSA-mqqv-chpx-vq25
Type: github-advisory

## Affected
- Go: `github.com/russellhaering/goxmldsig` — affected >=0 <1.1.1
- Go: `github.com/russellhaering/gosaml2` — affected >=0 <0.7.0

## Details
This affects all versions of package github.com/russellhaering/goxmldsig prior to 1.1.1. There is a crash on nil-pointer dereference caused by sending malformed XML signatures. This issue is patched in version 1.1.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7711
- https://github.com/russellhaering/gosaml2/issues/59
- https://github.com/russellhaering/goxmldsig/issues/48
- https://github.com/russellhaering/goxmldsig
- https://pkg.go.dev/vuln/GO-2020-0046
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMRUSSELLHAERINGGOXMLDSIG-608301
