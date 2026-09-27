# [H] Quadratic complexity when parsing some invalid inputs in encoding/pem

## Summary
Severity: High
Advisory: BIT-golang-2025-61723
Aliases: CVE-2025-61723, GO-2025-4009
Ecosystem: Bitnami
Published: 2025-11-06
Source: https://osv.dev/vulnerability/BIT-golang-2025-61723
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.25.0 <1.25.2

## Details
The processing time for parsing some invalid inputs scales non-linearly with respect to the size of the input. This affects programs which parse untrusted PEM inputs.

## References
- http://www.openwall.com/lists/oss-security/2025/10/08/1
- https://go.dev/cl/709858
- https://go.dev/issue/75676
- https://groups.google.com/g/golang-announce/c/4Emdl2iQ_bI
- https://nvd.nist.gov/vuln/detail/CVE-2025-61723
- https://pkg.go.dev/vuln/GO-2025-4009
