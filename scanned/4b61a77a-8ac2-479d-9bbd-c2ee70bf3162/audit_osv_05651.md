# [H] BIT-golang-2025-22865

## Summary
Severity: High
Advisory: BIT-golang-2025-22865
Aliases: CVE-2025-22865, GO-2025-3421
Ecosystem: Bitnami
Published: 2025-01-30
Source: https://osv.dev/vulnerability/BIT-golang-2025-22865
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.24.0-0 <1.24.0-rc.2

## Details
Using ParsePKCS1PrivateKey to parse a RSA key that is missing the CRT values would panic when verifying that the key is well formed.

## References
- https://go.dev/cl/643098
- https://go.dev/issue/71216
- https://groups.google.com/g/golang-dev/c/CAWXhan3Jww/m/bk9LAa-lCgAJ
- https://pkg.go.dev/vuln/GO-2025-3421
