# [H] Denial of service due to improper 100-continue handling in net/http

## Summary
Severity: High
Advisory: BIT-golang-2024-24791
Aliases: CVE-2024-24791, GO-2024-2963
Ecosystem: Bitnami
Published: 2024-07-04
Source: https://osv.dev/vulnerability/BIT-golang-2024-24791
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.22.0-0 <1.22.5

## Details
The net/http HTTP/1.1 client mishandled the case where a server responds to a request with an "Expect: 100-continue" header with a non-informational (200 or higher) status. This mishandling could leave a client connection in an invalid state, where the next request sent on the connection will fail. An attacker sending a request to a net/http/httputil.ReverseProxy proxy can exploit this mishandling to cause a denial of service by sending "Expect: 100-continue" requests which elicit a non-informational response from the backend. Each such request leaves the proxy with an invalid connection, and causes one subsequent request using that connection to fail.

## References
- https://go.dev/cl/591255
- https://go.dev/issue/67555
- https://groups.google.com/g/golang-dev/c/t0rK-qHBqzY/m/6MMoAZkMAgAJ
- https://pkg.go.dev/vuln/GO-2024-2963
- https://security.netapp.com/advisory/ntap-20241004-0004/
- https://nvd.nist.gov/vuln/detail/CVE-2024-24791
