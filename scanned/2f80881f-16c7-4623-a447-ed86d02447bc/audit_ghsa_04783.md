# [M] golang.org/x/crypto: Invoking memory leak when rejecting channels can lead to DoS

## Summary
Severity: Medium
Advisory: GHSA-qpw4-5x99-6vjp
CVE: CVE-2026-39827
CWE: CWE-924
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-qpw4-5x99-6vjp
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.52.0

## Details
An authenticated SSH client that repeatedly opened channels which were rejected by the server caused unbounded memory growth, eventually crashing the server process and affecting all connected users. Rejected channels are now properly removed from the connection's internal state and released for garbage collection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-39827
- https://cs.opensource.google/go/x/crypto
- https://go.dev/cl/781320
- https://go.dev/issue/35127
- https://groups.google.com/g/golang-announce/c/a082jnz-LvI
- https://pkg.go.dev/vuln/GO-2026-5016
