# [M] Panic in name constraint checking for malformed certificates in crypto/x509

## Summary
Severity: Medium
Advisory: BIT-golang-2026-27138
Aliases: CVE-2026-27138, GO-2026-4600
Ecosystem: Bitnami
Published: 2026-03-10
Source: https://osv.dev/vulnerability/BIT-golang-2026-27138
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.26.0-0 <1.26.1

## Details
Certificate verification can panic when a certificate in the chain has an empty DNS name and another certificate in the chain has excluded name constraints. This can crash programs that are either directly verifying X.509 certificate chains, or those that use TLS.

## References
- https://go.dev/cl/752183
- https://go.dev/issue/77953
- https://groups.google.com/g/golang-announce/c/EdhZqrQ98hk
- https://nvd.nist.gov/vuln/detail/CVE-2026-27138
- https://pkg.go.dev/vuln/GO-2026-4600
