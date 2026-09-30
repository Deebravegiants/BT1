# [H] Server-Side Request Forgery via Unrestricted HTTP Redirection in MCP Toolbox

## Summary
Severity: High
Advisory: CVE-2026-14540
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/CVE-2026-14540
Type: osv

## Details
A Server-Side Request Forgery (SSRF) vulnerability exists in the generic HTTP source and tool components of Google mcp-toolbox versions 0.3.0 through 1.4.0. While the toolbox implements baseline input sanitization for user-controlled parameters, the underlying HTTP client (internal/sources/http/http.go) fails to safely regulate request redirection boundaries. Specifically, the client is initialized without a restrictive CheckRedirect policy hook and lacks target IP validation. An attacker or a malicious data-driven prompt can supply a crafted path parameter that triggers an open redirect or a direct destination swap on the target backend, coercing the mcp-toolbox into blindly following the redirection and making unauthorized requests to internal or arbitrary external endpoints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14540.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-14540
- https://github.com/googleapis/mcp-toolbox/pull/3448
