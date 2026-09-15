# [H] Path traversal via Clean on Windows in path/filepath

## Summary
Severity: High
Advisory: BIT-golang-2022-29804
Aliases: CVE-2022-29804, GO-2022-0533
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-29804
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.18.0 <1.18.3

## Details
Incorrect conversion of certain invalid paths to valid, absolute paths in Clean in path/filepath before Go 1.17.11 and Go 1.18.3 on Windows allows potential directory traversal attack.

## References
- https://go.dev/cl/401595
- https://go.dev/issue/52476
- https://go.googlesource.com/go/+/9cd1818a7d019c02fa4898b3e45a323e35033290
- https://groups.google.com/g/golang-announce/c/TzIC9-t8Ytg/m/IWz5T6x7AAAJ
- https://pkg.go.dev/vuln/GO-2022-0533
- https://nvd.nist.gov/vuln/detail/CVE-2022-29804
