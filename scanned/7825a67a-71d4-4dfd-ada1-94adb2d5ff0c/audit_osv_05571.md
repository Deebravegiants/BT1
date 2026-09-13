# [H] BIT-golang-2021-27918

## Summary
Severity: High
Advisory: BIT-golang-2021-27918
Aliases: CVE-2021-27918, GO-2021-0234
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2021-27918
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.16.0 <1.16.1

## Details
encoding/xml in Go before 1.15.9 and 1.16.x before 1.16.1 has an infinite loop if a custom TokenReader (for xml.NewTokenDecoder) returns EOF in the middle of an element. This can occur in the Decode, DecodeElement, or Skip method.

## References
- https://groups.google.com/g/golang-announce/c/MfiLYjG-RAw
- https://security.gentoo.org/glsa/202208-02
- https://nvd.nist.gov/vuln/detail/CVE-2021-27918
