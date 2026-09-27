# [M] Excessive CPU consumption in Reader.ReadResponse in net/textproto

## Summary
Severity: Medium
Advisory: BIT-golang-2025-61724
Aliases: CVE-2025-61724, GO-2025-4015
Ecosystem: Bitnami
Published: 2025-11-06
Source: https://osv.dev/vulnerability/BIT-golang-2025-61724
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.25.0 <1.25.2

## Details
The Reader.ReadResponse function constructs a response string through repeated string concatenation of lines. When the number of lines in a response is large, this can cause excessive CPU consumption.

## References
- http://www.openwall.com/lists/oss-security/2025/10/08/1
- https://go.dev/cl/709859
- https://go.dev/issue/75716
- https://groups.google.com/g/golang-announce/c/4Emdl2iQ_bI
- https://nvd.nist.gov/vuln/detail/CVE-2025-61724
- https://pkg.go.dev/vuln/GO-2025-4015
