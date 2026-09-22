# [H] Stack exhaustion from deeply nested XML documents in encoding/xml

## Summary
Severity: High
Advisory: BIT-golang-2022-28131
Aliases: CVE-2022-28131, GO-2022-0521
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-28131
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.18.0 <1.18.4

## Details
Uncontrolled recursion in Decoder.Skip in encoding/xml before Go 1.17.12 and Go 1.18.4 allows an attacker to cause a panic due to stack exhaustion via a deeply nested XML document.

## References
- https://go.dev/cl/417062
- https://go.dev/issue/53614
- https://go.googlesource.com/go/+/08c46ed43d80bbb67cb904944ea3417989be4af3
- https://groups.google.com/g/golang-announce/c/nqrv9fbR0zE
- https://pkg.go.dev/vuln/GO-2022-0521
- https://nvd.nist.gov/vuln/detail/CVE-2022-28131
