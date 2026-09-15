# [M] Incorrect forwarding of sensitive headers and cookies on HTTP redirect in net/http

## Summary
Severity: Medium
Advisory: BIT-golang-2023-45289
Aliases: CVE-2023-45289, GO-2024-2600
Ecosystem: Bitnami
Published: 2024-03-12
Source: https://osv.dev/vulnerability/BIT-golang-2023-45289
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.22.0-0 <1.22.1

## Details
When following an HTTP redirect to a domain which is not a subdomain match or exact match of the initial domain, an http.Client does not forward sensitive headers such as "Authorization" or "Cookie". For example, a redirect from foo.com to www.foo.com will forward the Authorization header, but a redirect to bar.com will not. A maliciously crafted HTTP redirect could cause sensitive headers to be unexpectedly forwarded.

## References
- https://go.dev/cl/569340
- https://go.dev/issue/65065
- https://groups.google.com/g/golang-announce/c/5pwGVUPoMbg
- https://pkg.go.dev/vuln/GO-2024-2600
- https://security.netapp.com/advisory/ntap-20240329-0006/
- http://www.openwall.com/lists/oss-security/2024/03/08/4
- https://nvd.nist.gov/vuln/detail/CVE-2023-45289
