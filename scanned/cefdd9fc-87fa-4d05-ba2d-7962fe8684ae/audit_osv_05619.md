# [H] Improper sanitization of CSS values in html/template

## Summary
Severity: High
Advisory: BIT-golang-2023-24539
Aliases: CVE-2023-24539, GO-2023-1751
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2023-24539
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.20.0 <1.20.4

## Details
Angle brackets (<>) are not considered dangerous characters when inserted into CSS contexts. Templates containing multiple actions separated by a '/' character can result in unexpectedly closing the CSS context and allowing for injection of unexpected HTML, if executed with untrusted input.

## References
- https://go.dev/cl/491615
- https://go.dev/issue/59720
- https://groups.google.com/g/golang-announce/c/MEb0UyuSMsU
- https://pkg.go.dev/vuln/GO-2023-1751
- https://security.netapp.com/advisory/ntap-20241129-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2023-24539
