# [M] Sensitive headers not cleared on cross-origin redirect in net/http

## Summary
Severity: Medium
Advisory: BIT-golang-2025-4673
Aliases: CVE-2025-4673, GO-2025-3751
Ecosystem: Bitnami
Published: 2025-06-14
Source: https://osv.dev/vulnerability/BIT-golang-2025-4673
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.24.0-0 <1.24.4

## Details
Proxy-Authorization and Proxy-Authenticate headers persisted on cross-origin redirects potentially leaking sensitive information.

## References
- https://go.dev/cl/679257
- https://go.dev/issue/73816
- https://groups.google.com/g/golang-announce/c/ufZ8WpEsA3A
- https://nvd.nist.gov/vuln/detail/CVE-2025-4673
- https://pkg.go.dev/vuln/GO-2025-3751
