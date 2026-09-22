# [H] Infinite loop in parsing in go/scanner

## Summary
Severity: High
Advisory: BIT-golang-2023-24537
Aliases: CVE-2023-24537, GO-2023-1702
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2023-24537
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.20.0 <1.20.3

## Details
Calling any of the Parse functions on Go source code which contains //line directives with very large line numbers can cause an infinite loop due to integer overflow.

## References
- https://go.dev/cl/482078
- https://go.dev/issue/59180
- https://groups.google.com/g/golang-announce/c/Xdv6JL9ENs8
- https://pkg.go.dev/vuln/GO-2023-1702
- https://security.gentoo.org/glsa/202311-09
- https://security.netapp.com/advisory/ntap-20241129-0004/
- https://nvd.nist.gov/vuln/detail/CVE-2023-24537
