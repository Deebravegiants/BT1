# [H] Panic when validating certificates with DSA public keys in crypto/x509

## Summary
Severity: High
Advisory: BIT-golang-2025-58188
Aliases: CVE-2025-58188, GO-2025-4013
Ecosystem: Bitnami
Published: 2025-11-06
Source: https://osv.dev/vulnerability/BIT-golang-2025-58188
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.25.0 <1.25.2

## Details
Validating certificate chains which contain DSA public keys can cause programs to panic, due to a interface cast that assumes they implement the Equal method. This affects programs which validate arbitrary certificate chains.

## References
- http://www.openwall.com/lists/oss-security/2025/10/08/1
- https://go.dev/cl/709853
- https://go.dev/issue/75675
- https://groups.google.com/g/golang-announce/c/4Emdl2iQ_bI
- https://nvd.nist.gov/vuln/detail/CVE-2025-58188
- https://pkg.go.dev/vuln/GO-2025-4013
