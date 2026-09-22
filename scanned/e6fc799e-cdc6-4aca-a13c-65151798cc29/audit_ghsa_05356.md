# [M] golang.org/x/crypto: Invoking pathological inputs can lead to client panic

## Summary
Severity: Medium
Advisory: GHSA-9m57-25v3-79x9
CVE: CVE-2026-46598
CWE: CWE-129
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-9m57-25v3-79x9
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.52.0

## Details
For certain crafted inputs, a 'ed25519.PrivateKey' was created by casting malformed wire bytes, leading to a panic when used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-46598
- https://go.dev/cl/781360
- https://go.dev/issue/79596
- https://groups.google.com/g/golang-announce/c/a082jnz-LvI
- https://pkg.go.dev/vuln/GO-2026-5033
