# [M] Exposure of client IP addresses in net/http

## Summary
Severity: Medium
Advisory: BIT-golang-2022-32148
Aliases: CVE-2022-32148, GO-2022-0520
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-32148
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.18.0 <1.18.4

## Details
Improper exposure of client IP addresses in net/http before Go 1.17.12 and Go 1.18.4 can be triggered by calling httputil.ReverseProxy.ServeHTTP with a Request.Header map containing a nil value for the X-Forwarded-For header, which causes ReverseProxy to set the client IP as the value of the X-Forwarded-For header.

## References
- https://go.dev/cl/412857
- https://go.dev/issue/53423
- https://go.googlesource.com/go/+/b2cc0fecc2ccd80e6d5d16542cc684f97b3a9c8a
- https://groups.google.com/g/golang-announce/c/nqrv9fbR0zE
- https://pkg.go.dev/vuln/GO-2022-0520
- https://nvd.nist.gov/vuln/detail/CVE-2022-32148
