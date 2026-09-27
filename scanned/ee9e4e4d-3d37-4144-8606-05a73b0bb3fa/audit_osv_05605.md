# [H] Stack exhaustion when decoding certain messages in encoding/gob

## Summary
Severity: High
Advisory: BIT-golang-2022-30635
Aliases: CVE-2022-30635, GO-2022-0526
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-30635
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.18.0 <1.18.4

## Details
Uncontrolled recursion in Decoder.Decode in encoding/gob before Go 1.17.12 and Go 1.18.4 allows an attacker to cause a panic due to stack exhaustion via a message which contains deeply nested structures.

## References
- https://go.dev/cl/417064
- https://go.dev/issue/53615
- https://go.googlesource.com/go/+/6fa37e98ea4382bf881428ee0c150ce591500eb7
- https://groups.google.com/g/golang-announce/c/nqrv9fbR0zE
- https://pkg.go.dev/vuln/GO-2022-0526
- https://nvd.nist.gov/vuln/detail/CVE-2022-30635
