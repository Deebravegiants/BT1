# [M] Stack exhaustion due to deeply nested types in go/parser

## Summary
Severity: Medium
Advisory: BIT-golang-2022-1962
Aliases: CVE-2022-1962, GO-2022-0515
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-1962
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.18.0 <1.18.4

## Details
Uncontrolled recursion in the Parse functions in go/parser before Go 1.17.12 and Go 1.18.4 allow an attacker to cause a panic due to stack exhaustion via deeply nested types or declarations.

## References
- https://go.dev/cl/417063
- https://go.dev/issue/53616
- https://go.googlesource.com/go/+/695be961d57508da5a82217f7415200a11845879
- https://groups.google.com/g/golang-announce/c/nqrv9fbR0zE
- https://pkg.go.dev/vuln/GO-2022-0515
- https://nvd.nist.gov/vuln/detail/CVE-2022-1962
