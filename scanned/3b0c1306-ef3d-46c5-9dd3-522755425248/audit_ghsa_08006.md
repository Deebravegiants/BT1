# [M] golang.org/x/net/html has a Quadratic Parsing Complexity issue

## Summary
Severity: Medium
Advisory: GHSA-w4gw-w5jq-g9jh
CVE: CVE-2025-47911
CWE: CWE-407
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-02-12
Source: https://github.com/advisories/GHSA-w4gw-w5jq-g9jh
Type: github-advisory

## Affected
- Go: `golang.org/x/net/html` — affected >=0 <0.45.0

## Details
The html.Parse function in golang.org/x/net/html has quadratic parsing complexity when processing certain inputs, which can lead to Denial of Service (DoS) if an attacker provides specially crafted HTML content.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-47911
- https://github.com/golang/vulndb/issues/4440
- https://go.dev/cl/709876
- https://go.googlesource.com/net
- https://groups.google.com/g/golang-announce/c/jnQcOYpiR2c
- https://pkg.go.dev/vuln/GO-2026-4440
