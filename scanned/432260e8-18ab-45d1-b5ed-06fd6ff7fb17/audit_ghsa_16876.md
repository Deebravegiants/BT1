# [M] net/http, x/net/http2: close connections when receiving too many headers

## Summary
Severity: Medium
Advisory: GHSA-4v7x-pqxf-cx7m
CVE: CVE-2023-45288
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-04-04
Source: https://github.com/advisories/GHSA-4v7x-pqxf-cx7m
Type: github-advisory

## Affected
- Go: `net/http` — affected >=0 <1.21.9
- Go: `golang.org/x/net/http2` — affected >=0 <0.23.0
- Go: `net/http` — affected >=1.22.0-0 <1.22.2
- Go: `golang.org/x/net` — affected >=0 <0.23.0

## Details
An attacker may cause an HTTP/2 endpoint to read arbitrary amounts of header data by sending an excessive number of CONTINUATION frames. Maintaining HPACK state requires parsing and processing all HEADERS and CONTINUATION frames on a connection. When a request's headers exceed MaxHeaderBytes, no memory is allocated to store the excess headers, but they are still parsed. This permits an attacker to cause an HTTP/2 endpoint to read arbitrary amounts of header data, all associated with a request which is going to be rejected. These headers can include Huffman-encoded data which is significantly more expensive for the receiver to decode than for an attacker to send. The fix sets a limit on the amount of excess header frames we will process before closing a connection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-45288
- https://go.dev/cl/576155
- https://go.dev/issue/65051
- https://groups.google.com/g/golang-announce/c/YgW0sx8mN3M
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QRYFHIQ6XRKRYBI2F5UESH67BJBQXUPT
- https://nowotarski.info/http2-continuation-flood-technical-details
- https://pkg.go.dev/vuln/GO-2024-2687
- https://security.netapp.com/advisory/ntap-20240419-0009
- https://www.kb.cert.org/vuls/id/421644
- http://www.openwall.com/lists/oss-security/2024/04/03/16
- http://www.openwall.com/lists/oss-security/2024/04/05/4
