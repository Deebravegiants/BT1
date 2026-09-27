# [M] CrossOriginProtection insecure bypass patterns not limited to exact matches in net/http

## Summary
Severity: Medium
Advisory: BIT-golang-2025-47910
Aliases: CVE-2025-47910, GO-2025-3955
Ecosystem: Bitnami
Published: 2025-09-24
Source: https://osv.dev/vulnerability/BIT-golang-2025-47910
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.25.0 <1.25.1

## Details
When using http.CrossOriginProtection, the AddInsecureBypassPattern method can unexpectedly bypass more requests than intended. CrossOriginProtection then skips validation, but forwards the original request path, which may be served by a different handler without the intended security protections.

## References
- https://go.dev/cl/699275
- https://go.dev/issue/75054
- https://groups.google.com/g/golang-announce/c/PtW9VW21NPs/m/DJhMQ-m5AQAJ
- https://nvd.nist.gov/vuln/detail/CVE-2025-47910
- https://pkg.go.dev/vuln/GO-2025-3955
