# [H] Non-linear parsing of case-insensitive content in golang.org/x/net/html

## Summary
Severity: High
Advisory: GHSA-w32m-9786-jp63
CVE: CVE-2024-45338
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-12-18
Source: https://github.com/advisories/GHSA-w32m-9786-jp63
Type: github-advisory

## Affected
- Go: `golang.org/x/net/html` — affected >=0 <0.33.0

## Details
An attacker can craft an input to the Parse functions that would be processed non-linearly with respect to its length, resulting in extremely slow parsing. This could cause a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45338
- https://github.com/golang/go/issues/70906
- https://cs.opensource.google/go/x/net
- https://go.dev/cl/637536
- https://go.dev/issue/70906
- https://groups.google.com/g/golang-announce/c/wSCRmFnNmPA/m/Lvcd0mRMAwAJ
- https://pkg.go.dev/vuln/GO-2024-3333
