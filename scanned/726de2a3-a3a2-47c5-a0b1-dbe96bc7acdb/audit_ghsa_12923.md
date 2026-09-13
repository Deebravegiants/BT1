# [H] golang.org/x/net/http2/h2c vulnerable to request smuggling attack

## Summary
Severity: High
Advisory: GHSA-fxg5-wq6x-vr4w
CVE: CVE-2022-41721
CWE: CWE-444
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-01-14
Source: https://github.com/advisories/GHSA-fxg5-wq6x-vr4w
Type: github-advisory

## Affected
- Go: `golang.org/x/net` — affected >=0.0.0-20220524220425-1d687d428aca <0.1.1-0.20221104162952-702349b0e862

## Details
A request smuggling attack is possible when using MaxBytesHandler. When using MaxBytesHandler, the body of an HTTP request is not fully consumed. When the server attempts to read HTTP2 frames from the connection, it will instead be reading the body of the HTTP request, which could be attacker-manipulated to represent arbitrary HTTP2 requests.

### Specific Go Packages Affected
golang.org/x/net/http2/h2c

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41721
- https://cs.opensource.google/go/x/net
- https://go.dev/cl/447396
- https://go.dev/issue/56352
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/X3H3EWQXM2XL5AGBX6UL443JEJ3GQXJN
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/X5DXTLLWN6HKI5I35EUZRBISTNZJ75GP
- https://pkg.go.dev/vuln/GO-2023-1495
