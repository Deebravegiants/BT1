# [M] Improper sanitization of Transfer-Encoding headers in net/http

## Summary
Severity: Medium
Advisory: BIT-golang-2022-1705
Aliases: CVE-2022-1705, GO-2022-0525
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-1705
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.18.0 <1.18.4

## Details
Acceptance of some invalid Transfer-Encoding headers in the HTTP/1 client in net/http before Go 1.17.12 and Go 1.18.4 allows HTTP request smuggling if combined with an intermediate server that also improperly fails to reject the header as invalid.

## References
- https://go.dev/cl/409874
- https://go.dev/cl/410714
- https://go.dev/issue/53188
- https://go.googlesource.com/go/+/e5017a93fcde94f09836200bca55324af037ee5f
- https://groups.google.com/g/golang-announce/c/nqrv9fbR0zE
- https://pkg.go.dev/vuln/GO-2022-0525
- https://nvd.nist.gov/vuln/detail/CVE-2022-1705
