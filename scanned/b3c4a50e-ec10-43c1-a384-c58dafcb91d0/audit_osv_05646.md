# [H] Stack exhaustion in Decoder.Decode in encoding/gob

## Summary
Severity: High
Advisory: BIT-golang-2024-34156
Aliases: CVE-2024-34156, GO-2024-3106
Ecosystem: Bitnami
Published: 2024-09-10
Source: https://osv.dev/vulnerability/BIT-golang-2024-34156
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.23.0-0 <1.23.1

## Details
Calling Decoder.Decode on a message which contains deeply nested structures can cause a panic due to stack exhaustion. This is a follow-up to CVE-2022-30635.

## References
- https://go.dev/cl/611239
- https://go.dev/issue/69139
- https://groups.google.com/g/golang-dev/c/S9POB9NCTdk
- https://pkg.go.dev/vuln/GO-2024-3106
- https://security.netapp.com/advisory/ntap-20240926-0004/
- https://nvd.nist.gov/vuln/detail/CVE-2024-34156
