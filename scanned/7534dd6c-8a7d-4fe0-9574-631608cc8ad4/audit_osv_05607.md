# [H] Panic when decoding Float and Rat types in math/big

## Summary
Severity: High
Advisory: BIT-golang-2022-32189
Aliases: CVE-2022-32189, GO-2022-0537
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-32189
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.18.0 <1.18.5

## Details
A too-short encoded message can cause a panic in Float.GobDecode and Rat GobDecode in math/big in Go before 1.17.13 and 1.18.5, potentially allowing a denial of service.

## References
- https://go.dev/cl/417774
- https://go.dev/issue/53871
- https://go.googlesource.com/go/+/055113ef364337607e3e72ed7d48df67fde6fc66
- https://groups.google.com/g/golang-announce/c/YqYYG87xB10
- https://pkg.go.dev/vuln/GO-2022-0537
- https://nvd.nist.gov/vuln/detail/CVE-2022-32189
