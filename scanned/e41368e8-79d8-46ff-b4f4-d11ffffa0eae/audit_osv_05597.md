# [H] Incorrect sanitization of forwarded query parameters in net/http/httputil

## Summary
Severity: High
Advisory: BIT-golang-2022-2880
Aliases: CVE-2022-2880, GO-2022-1038
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-2880
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.19.0 <1.19.2

## Details
Requests forwarded by ReverseProxy include the raw query parameters from the inbound request, including unparsable parameters rejected by net/http. This could permit query parameter smuggling when a Go proxy forwards a parameter with an unparsable value. After fix, ReverseProxy sanitizes the query parameters in the forwarded query when the outbound request's Form field is set after the ReverseProxy. Director function returns, indicating that the proxy has parsed the query parameters. Proxies which do not parse query parameters continue to forward the original query parameters unchanged.

## References
- https://go.dev/cl/432976
- https://go.dev/issue/54663
- https://groups.google.com/g/golang-announce/c/xtuG5faxtaU
- https://pkg.go.dev/vuln/GO-2022-1038
- https://security.gentoo.org/glsa/202311-09
- https://nvd.nist.gov/vuln/detail/CVE-2022-2880
