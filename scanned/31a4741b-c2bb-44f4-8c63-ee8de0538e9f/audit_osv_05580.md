# [H] BIT-golang-2021-33198

## Summary
Severity: High
Advisory: BIT-golang-2021-33198
Aliases: CVE-2021-33198, GO-2021-0242
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2021-33198
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.16.0 <1.16.5

## Details
In Go before 1.15.13 and 1.16.x before 1.16.5, there can be a panic for a large exponent to the math/big.Rat SetString or UnmarshalText method.

## References
- https://groups.google.com/g/golang-announce
- https://groups.google.com/g/golang-announce/c/RgCMkAEQjSI
- https://security.gentoo.org/glsa/202208-02
- https://nvd.nist.gov/vuln/detail/CVE-2021-33198
