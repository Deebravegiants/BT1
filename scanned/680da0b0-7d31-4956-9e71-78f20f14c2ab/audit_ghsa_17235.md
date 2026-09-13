# [H] Model Context Protocol (MCP) Python SDK does not enable DNS rebinding protection by default

## Summary
Severity: High
Advisory: GHSA-9h52-p55h-vw2f
CVE: CVE-2025-66416
CWE: CWE-1188, CWE-350
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-9h52-p55h-vw2f
Type: github-advisory

## Affected
- PyPI: `mcp` — affected >=0 <1.23.0

## Details
### Description

The Model Context Protocol (MCP) Python SDK does not enable DNS rebinding protection by default for HTTP-based servers. When an HTTP-based MCP server is run on localhost without authentication using `FastMCP` with streamable HTTP or SSE transport, and has not configured `TransportSecuritySettings`, a malicious website could exploit DNS rebinding to bypass same-origin policy restrictions and send requests to the local MCP server. This could allow an attacker to invoke tools or access resources exposed by the MCP server on behalf of the user in those limited circumstances.

Note that running HTTP-based MCP servers locally without authentication is not recommended per MCP security best practices. This issue does not affect servers using stdio transport.

Servers created via `FastMCP()` now have DNS rebinding protection enabled by default when the `host` parameter is `127.0.0.1` or `localhost`. Users are advised to update to version `1.23.0` to receive this automatic protection. Users with custom low-level server configurations using `StreamableHTTPSessionManager` or `SseServerTransport` directly should explicitly configure `TransportSecuritySettings` when running an unauthenticated server on localhost.

## References
- https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-9h52-p55h-vw2f
- https://nvd.nist.gov/vuln/detail/CVE-2025-66416
- https://github.com/modelcontextprotocol/python-sdk/commit/d3a184119e4479ea6a63590bc41f01dc06e3fa99
- https://github.com/advisories/GHSA-9h52-p55h-vw2f
- https://github.com/modelcontextprotocol/python-sdk
- https://github.com/pypa/advisory-database/tree/main/vulns/mcp/PYSEC-2026-1617.yaml
- https://pypi.org/project/mcp
