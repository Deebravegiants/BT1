# [C] Improper handling of JavaScript whitespace in html/template

## Summary
Severity: Critical
Advisory: BIT-golang-2023-24540
Aliases: CVE-2023-24540, GO-2023-1752
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2023-24540
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.20.0 <1.20.4

## Details
Not all valid JavaScript whitespace characters are considered to be whitespace. Templates containing whitespace characters outside of the character set "\t\n\f\r\u0020\u2028\u2029" in JavaScript contexts that also contain actions may not be properly sanitized during execution.

## References
- https://go.dev/cl/491616
- https://go.dev/issue/59721
- https://groups.google.com/g/golang-announce/c/MEb0UyuSMsU
- https://pkg.go.dev/vuln/GO-2023-1752
- https://security.netapp.com/advisory/ntap-20241115-0008/
- https://nvd.nist.gov/vuln/detail/CVE-2023-24540
