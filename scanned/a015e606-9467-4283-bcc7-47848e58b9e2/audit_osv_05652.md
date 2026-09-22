# [M] Timing sidechannel for P-256 on ppc64le in crypto/internal/nistec

## Summary
Severity: Medium
Advisory: BIT-golang-2025-22866
Aliases: CVE-2025-22866, GO-2025-3447
Ecosystem: Bitnami
Published: 2025-02-08
Source: https://osv.dev/vulnerability/BIT-golang-2025-22866
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.24.0-0 <1.24.0

## Details
Due to the usage of a variable time instruction in the assembly implementation of an internal function, a small number of bits of secret scalars are leaked on the ppc64le architecture. Due to the way this function is used, we do not believe this leakage is enough to allow recovery of the private key when P-256 is used in any well known protocols.

## References
- https://go.dev/cl/643735
- https://go.dev/issue/71383
- https://groups.google.com/g/golang-announce/c/xU1ZCHUZw3k
- https://pkg.go.dev/vuln/GO-2025-3447
- https://security.netapp.com/advisory/ntap-20250221-0002/
- https://nvd.nist.gov/vuln/detail/CVE-2025-22866
