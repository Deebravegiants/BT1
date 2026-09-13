# [M] Incorrect calculation on P256 curves in crypto/internal/nistec

## Summary
Severity: Medium
Advisory: BIT-golang-2023-24532
Aliases: CVE-2023-24532, GO-2023-1621
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2023-24532
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.20.0 <1.20.2

## Details
The ScalarMult and ScalarBaseMult methods of the P256 Curve may return an incorrect result if called with some specific unreduced scalars (a scalar larger than the order of the curve). This does not impact usages of crypto/ecdsa or crypto/ecdh.

## References
- https://go.dev/cl/471255
- https://go.dev/issue/58647
- https://groups.google.com/g/golang-announce/c/3-TpUx48iQY
- https://pkg.go.dev/vuln/GO-2023-1621
- https://security.netapp.com/advisory/ntap-20230331-0011/
- https://nvd.nist.gov/vuln/detail/CVE-2023-24532
