# [M] ReverseProxy forwards queries with more than urlmaxqueryparams parameters in net/http/httputil

## Summary
Severity: Medium
Advisory: BIT-golang-2026-39825
Aliases: CVE-2026-39825, GO-2026-4976
Ecosystem: Bitnami
Published: 2026-05-11
Source: https://osv.dev/vulnerability/BIT-golang-2026-39825
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.26.0-0 <1.26.3

## Details
ReverseProxy can forward queries containing parameters not visible to Rewrite functions. When used with a Rewrite function, or a Director function which parses query parameters, ReverseProxy sanitizes the forwarded request to remove query parameters which are not parsed by url.ParseQuery. ReverseProxy does not take ParseQuery's limit on the total number of query parameters (controlled by GODEBUG=urlmaxqueryparams=N) into account. This can permit ReverseProxy to forward a request containing a query parameter that is not visible to the Rewrite function. For example, the query "a1=x&a2=x&...&a10000=x&hidden=y" can forward the parameter "hidden=y" while hiding it from the proxy's Rewrite function.

## References
- https://go.dev/cl/770541
- https://go.dev/issue/78948
- https://groups.google.com/g/golang-announce/c/qcCIEXso47M
- https://nvd.nist.gov/vuln/detail/CVE-2026-39825
- https://pkg.go.dev/vuln/GO-2026-4976
