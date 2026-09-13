# [M] cpp-httplib: Use-after-free of TLS session in WebSocketClient::shutdown_and_close()

## Summary
Severity: Medium
Advisory: CVE-2026-77358
Aliases: GHSA-w7p7-f35j-mw7q
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-77358
Type: osv

## Details
cpp-httplib is a C++ header-only HTTP/HTTPS library. In versions 0.33.0 through 0.50.0, the TLS-enabled WebSocket client frees the TLS session before closing the WebSocket that still uses it, producing a use-after-free. In WebSocketClient::shutdown_and_close the SSL object is freed and the pointer cleared, but the subsequent WebSocket close still sends a close frame through the SSL socket stream, which holds a raw copy of the now-dangling session pointer and reads from and writes to the freed memory. The same freed-then-used ordering is reachable through the client's destructor and its connect path, so ordinary teardown of a secure WebSocket connection triggers the defect. This issue is fixed in version 0.50.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77358.json
- https://github.com/yhirose/cpp-httplib/security/advisories/GHSA-w7p7-f35j-mw7q
- https://nvd.nist.gov/vuln/detail/CVE-2026-77358
- https://github.com/yhirose/cpp-httplib/commit/2f986fd5e56e7c5f686d965174516360930f371d
