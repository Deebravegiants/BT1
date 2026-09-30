# [H] Quadratic complexity when checking name constraints in crypto/x509

## Summary
Severity: High
Advisory: BIT-golang-2025-58187
Aliases: CVE-2025-58187, GO-2025-4007
Ecosystem: Bitnami
Published: 2025-11-06
Source: https://osv.dev/vulnerability/BIT-golang-2025-58187
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.25.0 <1.25.3

## Details
Due to the design of the name constraint checking algorithm, the processing time of some inputs scale non-linearly with respect to the size of the certificate. This affects programs which validate arbitrary certificate chains.

## References
- http://www.openwall.com/lists/oss-security/2025/10/08/1
- https://go.dev/cl/709854
- https://go.dev/issue/75681
- https://groups.google.com/g/golang-announce/c/4Emdl2iQ_bI
- https://nvd.nist.gov/vuln/detail/CVE-2025-58187
- https://pkg.go.dev/vuln/GO-2025-4007
