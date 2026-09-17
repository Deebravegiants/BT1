# [M] mcp-use Inspector Proxy Server-Side Request Forgery via Caller-Supplied Target URL

## Summary
Severity: Medium
Advisory: CVE-2026-81091
Aliases: GHSA-f2jg-rm2x-hc5p
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81091
Type: osv

## Details
The proxy middleware in mcp-use's inspector forwards requests to a destination the caller names. mountMcpProxy in libraries/typescript/packages/inspector/src/server/proxy/mcp-proxy.ts read the target from the X-Target-URL header or the __mcp_target parameter and proxied to it without inspecting the host, so loopback, link-local and private addresses were all accepted, as were names that resolve to them, and the validation was not reapplied to a redirect the destination returned. A caller could therefore make the server issue requests to addresses reachable only from the host it runs on and read the responses. The current code calls isSafeProxyTarget, which checks the resolved address against private, loopback and link-local ranges before proxying and bounds the number of redirects followed.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81091.json
- https://github.com/mcp-use/mcp-use/security/advisories/GHSA-f2jg-rm2x-hc5p
- https://nvd.nist.gov/vuln/detail/CVE-2026-81091
- https://www.vulncheck.com/advisories/mcp-use-inspector-proxy-server-side-request-forgery-via-caller-supplied-target-url
- https://github.com/mcp-use/mcp-use
