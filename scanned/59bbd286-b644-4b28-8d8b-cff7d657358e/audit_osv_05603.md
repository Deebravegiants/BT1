# [H] Stack exhaustion when unmarshaling certain documents in encoding/xml

## Summary
Severity: High
Advisory: BIT-golang-2022-30633
Aliases: CVE-2022-30633, GO-2022-0523
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-30633
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.18.0 <1.18.4

## Details
Uncontrolled recursion in Unmarshal in encoding/xml before Go 1.17.12 and Go 1.18.4 allows an attacker to cause a panic due to stack exhaustion via unmarshalling an XML document into a Go struct which has a nested field that uses the 'any' field tag.

## References
- https://go.dev/cl/417061
- https://go.dev/issue/53611
- https://go.googlesource.com/go/+/c4c1993fd2a5b26fe45c09592af6d3388a3b2e08
- https://groups.google.com/g/golang-announce/c/nqrv9fbR0zE
- https://pkg.go.dev/vuln/GO-2022-0523
- https://nvd.nist.gov/vuln/detail/CVE-2022-30633
