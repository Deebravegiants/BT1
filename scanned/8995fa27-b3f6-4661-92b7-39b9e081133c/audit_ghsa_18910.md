# [M] golang.org/x/crypto/ssh allows an attacker to cause unbounded memory consumption

## Summary
Severity: Medium
Advisory: GHSA-j5w8-q4qc-rx2x
CVE: CVE-2025-58181
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-11-19
Source: https://github.com/advisories/GHSA-j5w8-q4qc-rx2x
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.45.0

## Details
SSH servers parsing GSSAPI authentication requests do not validate the number of mechanisms specified in the request, allowing an attacker to cause unbounded memory consumption.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-58181
- https://go.dev/cl/721961
- https://go.dev/issue/76363
- https://groups.google.com/g/golang-announce/c/w-oX3UxNcZA
- https://pkg.go.dev/vuln/GO-2025-4134
