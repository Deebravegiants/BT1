# [H] Excessive CPU consumption in ParseAddress in net/mail

## Summary
Severity: High
Advisory: BIT-golang-2025-61725
Aliases: CVE-2025-61725, GO-2025-4006
Ecosystem: Bitnami
Published: 2025-11-06
Source: https://osv.dev/vulnerability/BIT-golang-2025-61725
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.25.0 <1.25.2

## Details
The ParseAddress function constructs domain-literal address components through repeated string concatenation. When parsing large domain-literal components, this can cause excessive CPU consumption.

## References
- http://www.openwall.com/lists/oss-security/2025/10/08/1
- https://go.dev/cl/709860
- https://go.dev/issue/75680
- https://groups.google.com/g/golang-announce/c/4Emdl2iQ_bI
- https://nvd.nist.gov/vuln/detail/CVE-2025-61725
- https://pkg.go.dev/vuln/GO-2025-4006
