# [M] Improper application of excluded DNS name constraints when verifying wildcard names in crypto/x509

## Summary
Severity: Medium
Advisory: BIT-golang-2025-61727
Aliases: CVE-2025-61727, GO-2025-4175
Ecosystem: Bitnami
Published: 2025-12-06
Source: https://osv.dev/vulnerability/BIT-golang-2025-61727
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.25.0 <1.25.5

## Details
An excluded subdomain constraint in a certificate chain does not restrict the usage of wildcard SANs in the leaf certificate. For example a constraint that excludes the subdomain test.example.com does not prevent a leaf certificate from claiming the SAN *.example.com.

## References
- https://go.dev/cl/723900
- https://go.dev/issue/76442
- https://groups.google.com/g/golang-announce/c/8FJoBkPddm4
- https://nvd.nist.gov/vuln/detail/CVE-2025-61727
- https://pkg.go.dev/vuln/GO-2025-4175
