# [H] Indefinite hang with large buffers on Windows in crypto/rand

## Summary
Severity: High
Advisory: BIT-golang-2022-30634
Aliases: CVE-2022-30634, GO-2022-0477
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-30634
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.18.0 <1.18.3

## Details
Infinite loop in Read in crypto/rand before Go 1.17.11 and Go 1.18.3 on Windows allows attacker to cause an indefinite hang by passing a buffer larger than 1 << 32 - 1 bytes.

## References
- https://go.dev/cl/402257
- https://go.dev/issue/52561
- https://go.googlesource.com/go/+/bb1f4416180511231de6d17a1f2f55c82aafc863
- https://groups.google.com/g/golang-announce/c/TzIC9-t8Ytg/m/IWz5T6x7AAAJ
- https://pkg.go.dev/vuln/GO-2022-0477
- https://nvd.nist.gov/vuln/detail/CVE-2022-30634
