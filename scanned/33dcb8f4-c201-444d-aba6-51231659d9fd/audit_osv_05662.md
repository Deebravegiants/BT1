# [M] Lack of limit when parsing cookies can cause memory exhaustion in net/http

## Summary
Severity: Medium
Advisory: BIT-golang-2025-58186
Aliases: CVE-2025-58186, GO-2025-4012
Ecosystem: Bitnami
Published: 2025-11-06
Source: https://osv.dev/vulnerability/BIT-golang-2025-58186
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.25.0 <1.25.2

## Details
Despite HTTP headers having a default limit of 1MB, the number of cookies that can be parsed does not have a limit. By sending a lot of very small cookies such as "a=;", an attacker can make an HTTP server allocate a large amount of structs, causing large memory consumption.

## References
- http://www.openwall.com/lists/oss-security/2025/10/08/1
- https://go.dev/cl/709855
- https://go.dev/issue/75672
- https://groups.google.com/g/golang-announce/c/4Emdl2iQ_bI
- https://nvd.nist.gov/vuln/detail/CVE-2025-58186
- https://pkg.go.dev/vuln/GO-2025-4012
