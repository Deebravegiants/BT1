# [H] cortex establishes TLS connections with `InsecureSkipVerify` set to `true`

## Summary
Severity: High
Advisory: GHSA-vw7g-3cc7-7rmh
CVE: CVE-2024-41265
CWE: CWE-599
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-08-01
Source: https://github.com/advisories/GHSA-vw7g-3cc7-7rmh
Type: github-advisory

## Affected
- Go: `github.com/cortexproject/cortex` — affected >=0

## Details
A TLS certificate verification issue discovered in cortex v0.42.1 allows attackers to obtain sensitive information via the makeOperatorRequest function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41265
- https://gist.github.com/nyxfqq/1a8237f3f9cf793c6433f08b17d1593c
- https://github.com/advisories/GHSA-vw7g-3cc7-7rmh
- https://github.com/cortexproject/cortex
- https://pkg.go.dev/vuln/GO-2024-3036
