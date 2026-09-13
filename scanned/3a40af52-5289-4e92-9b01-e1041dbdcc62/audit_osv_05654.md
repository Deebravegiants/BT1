# [H] Usage of ExtKeyUsageAny disables policy validation in crypto/x509

## Summary
Severity: High
Advisory: BIT-golang-2025-22874
Aliases: CVE-2025-22874, GO-2025-3749
Ecosystem: Bitnami
Published: 2025-06-14
Source: https://osv.dev/vulnerability/BIT-golang-2025-22874
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.24.0-0 <1.24.4

## Details
Calling Verify with a VerifyOptions.KeyUsages that contains ExtKeyUsageAny unintentionally disabledpolicy validation. This only affected certificate chains which contain policy graphs, which are rather uncommon.

## References
- https://go.dev/cl/670375
- https://go.dev/issue/73612
- https://groups.google.com/g/golang-announce/c/ufZ8WpEsA3A
- https://nvd.nist.gov/vuln/detail/CVE-2025-22874
- https://pkg.go.dev/vuln/GO-2025-3749
