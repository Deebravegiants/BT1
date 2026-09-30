# [H] golang.org/x/crypto: Invoking byte arithmetic causes underflow and panic

## Summary
Severity: High
Advisory: GHSA-q4h4-gmj2-qvw2
CVE: CVE-2026-46597
CWE: CWE-704
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-q4h4-gmj2-qvw2
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.52.0

## Details
An incorrectly placed cast from bytes to int allowed for server-side panic in the AES-GCM packet decoder for well-crafted inputs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-46597
- https://cs.opensource.google/go/x/crypto
- https://go.dev/cl/781620
- https://go.dev/issue/79561
- https://groups.google.com/g/golang-announce/c/a082jnz-LvI
- https://pkg.go.dev/vuln/GO-2026-5013
