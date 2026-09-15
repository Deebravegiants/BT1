# [M] Stack exhaustion in all Parse functions in go/parser

## Summary
Severity: Medium
Advisory: BIT-golang-2024-34155
Aliases: CVE-2024-34155, GO-2024-3105
Ecosystem: Bitnami
Published: 2024-09-10
Source: https://osv.dev/vulnerability/BIT-golang-2024-34155
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.23.0-0 <1.23.1

## Details
Calling any of the Parse functions on Go source code which contains deeply nested literals can cause a panic due to stack exhaustion.

## References
- https://go.dev/cl/611238
- https://go.dev/issue/69138
- https://groups.google.com/g/golang-dev/c/S9POB9NCTdk
- https://pkg.go.dev/vuln/GO-2024-3105
- https://security.netapp.com/advisory/ntap-20240926-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2024-34155
