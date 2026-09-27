# [M] Usage of IPv6 zone IDs can bypass URI name constraints in crypto/x509

## Summary
Severity: Medium
Advisory: BIT-golang-2024-45341
Aliases: CVE-2024-45341, GO-2025-3373
Ecosystem: Bitnami
Published: 2025-01-30
Source: https://osv.dev/vulnerability/BIT-golang-2024-45341
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.24.0-0 <1.24.0

## Details
A certificate with a URI which has a IPv6 address with a zone ID may incorrectly satisfy a URI name constraint that applies to the certificate chain. Certificates containing URIs are not permitted in the web PKI, so this only affects users of private PKIs which make use of URIs.

## References
- https://go.dev/cl/643099
- https://go.dev/issue/71156
- https://groups.google.com/g/golang-dev/c/CAWXhan3Jww/m/bk9LAa-lCgAJ
- https://groups.google.com/g/golang-dev/c/bG8cv1muIBM/m/G461hA6lCgAJ
- https://pkg.go.dev/vuln/GO-2025-3373
- https://security.netapp.com/advisory/ntap-20250221-0004/
- https://nvd.nist.gov/vuln/detail/CVE-2024-45341
