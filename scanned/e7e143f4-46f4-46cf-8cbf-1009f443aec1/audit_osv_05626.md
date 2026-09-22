# [M] Insufficient sanitization of Host header in net/http

## Summary
Severity: Medium
Advisory: BIT-golang-2023-29406
Aliases: CVE-2023-29406, GO-2023-1878
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2023-29406
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.20.0 <1.20.6

## Details
The HTTP/1 client does not fully validate the contents of the Host header. A maliciously crafted Host header can inject additional headers or entire requests. With fix, the HTTP/1 client now refuses to send requests containing an invalid Request.Host or Request.URL.Host value.

## References
- https://go.dev/cl/506996
- https://go.dev/issue/60374
- https://groups.google.com/g/golang-announce/c/2q13H6LEEx0
- https://pkg.go.dev/vuln/GO-2023-1878
- https://security.gentoo.org/glsa/202311-09
- https://security.netapp.com/advisory/ntap-20230814-0002/
- https://nvd.nist.gov/vuln/detail/CVE-2023-29406
