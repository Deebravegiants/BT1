# [H] Excessive resource consumption when printing error string for host certificate validation in crypto/x509

## Summary
Severity: High
Advisory: BIT-golang-2025-61729
Aliases: CVE-2025-61729, GO-2025-4155
Ecosystem: Bitnami
Published: 2025-12-04
Source: https://osv.dev/vulnerability/BIT-golang-2025-61729
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.25.0 <1.25.5

## Details
Within HostnameError.Error(), when constructing an error string, there is no limit to the number of hosts that will be printed out. Furthermore, the error string is constructed by repeated string concatenation, leading to quadratic runtime. Therefore, a certificate provided by a malicious actor can result in excessive resource consumption.

## References
- https://go.dev/cl/725920
- https://go.dev/issue/76445
- https://groups.google.com/g/golang-announce/c/8FJoBkPddm4
- https://nvd.nist.gov/vuln/detail/CVE-2025-61729
- https://pkg.go.dev/vuln/GO-2025-4155
