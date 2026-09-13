# [M] Incorrect detection of reserved device names on Windows in path/filepath

## Summary
Severity: Medium
Advisory: BIT-golang-2023-45284
Aliases: CVE-2023-45284, GO-2023-2186
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2023-45284
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.21.0-0 <1.21.4

## Details
On Windows, The IsLocal function does not correctly detect reserved device names in some cases. Reserved names followed by spaces, such as "COM1 ", and reserved names "COM" and "LPT" followed by superscript 1, 2, or 3, are incorrectly reported as local. With fix, IsLocal now correctly reports these names as non-local.

## References
- https://go.dev/cl/540277
- https://go.dev/issue/63713
- https://groups.google.com/g/golang-announce/c/4tU8LZfBFkY
- https://pkg.go.dev/vuln/GO-2023-2186
- https://nvd.nist.gov/vuln/detail/CVE-2023-45284
