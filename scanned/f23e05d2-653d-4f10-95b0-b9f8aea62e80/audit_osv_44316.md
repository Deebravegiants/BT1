# [H] mcp-go before 0.56.0 Missing Host Header Validation Enables DNS Rebinding

## Summary
Severity: High
Advisory: CVE-2026-81092
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81092
Type: osv

## Details
mcp-go accepted requests on its HTTP transports without checking the Host header. StreamableHTTPServer.ServeHTTP in server/streamable_http.go and SSEServer.ServeHTTP in server/sse.go served any request arriving over a loopback connection regardless of the host it named, and the SSE transport's cross-origin default allowed any origin. A page in a browser could therefore point a name it controlled at the loopback address and reach a server listening there, invoking tools and reading resources that the server exposed on the assumption that only local software could connect. No release before 0.56.0 validated the header on either transport; 0.56.0 adds server/http_localhost.go, which rejects a loopback-bound request carrying a host that is not a loopback name, and wires it into both transports.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81092.json
- https://github.com/mark3labs/mcp-go/releases/tag/v0.56.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-81092
- https://www.vulncheck.com/advisories/mcp-go-before-0.56.0-missing-host-header-validation-enables-dns-rebinding
- https://github.com/mark3labs/mcp-go/pull/921
- https://github.com/mark3labs/mcp-go
