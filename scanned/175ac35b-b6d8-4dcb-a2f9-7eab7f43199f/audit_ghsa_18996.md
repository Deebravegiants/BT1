# [M] golang.org/x/crypto/ssh/agent vulnerable to panic if message is malformed due to out of bounds read

## Summary
Severity: Medium
Advisory: GHSA-f6x5-jh6r-wrfv
CVE: CVE-2025-47914
CWE: CWE-125
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-11-19
Source: https://github.com/advisories/GHSA-f6x5-jh6r-wrfv
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.45.0

## Details
SSH Agent servers do not validate the size of messages when processing new identity requests, which may cause the program to panic if the message is malformed due to an out of bounds read.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-47914
- https://go.dev/cl/721960
- https://go.dev/issue/76364
- https://go.googlesource.com/crypto
- https://groups.google.com/g/golang-announce/c/w-oX3UxNcZA
- https://pkg.go.dev/vuln/GO-2025-4135
