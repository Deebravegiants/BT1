# [C] mcp-remote exposed to OS command injection via untrusted MCP server connections

## Summary
Severity: Critical
Advisory: GHSA-6xpm-ggf7-wc3p
CVE: CVE-2025-6514
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-6xpm-ggf7-wc3p
Type: github-advisory

## Affected
- npm: `mcp-remote` — affected >=0.0.5 <0.1.16

## Details
mcp-remote is exposed to OS command injection when connecting to untrusted MCP servers due to crafted input from the authorization_endpoint response URL

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6514
- https://github.com/geelen/mcp-remote/commit/607b226a356cb61a239ffaba2fb3db1c9dea4bac
- https://github.com/geelen/mcp-remote
- https://jfrog.com/blog/2025-6514-critical-mcp-remote-rce-vulnerability
- https://research.jfrog.com/vulnerabilities/mcp-remote-command-injection-rce-jfsa-2025-001290844
