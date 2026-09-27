# [H] MCP Toolbox for Databases: authenticated authorization bypass

## Summary
Severity: High
Advisory: GHSA-5gf6-gc35-xjpc
CVE: CVE-2026-11719
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-5gf6-gc35-xjpc
Type: github-advisory

## Affected
- Go: `github.com/googleapis/mcp-toolbox` — affected >=0 <1.4.0

## Details
An authenticated authorization bypass vulnerability exists in MCP Toolbox for Databases due to missing scope enforcement across older protocol handlers.

While the 2025-11-25 protocol version handler correctly enforces per-tool restrictions defined by scopesRequired, older supported protocol versions (2025-06-18, 2025-03-26, and 2024-11-05) omit this check. An authenticated client with low-privilege tokens (e.g., read) can bypass the intended per-tool scope restrictions and execute high-privilege tools (e.g., admin) simply by specifying an older protocol version in the MCP-Protocol-Version header, or by omitting the header entirely (which causes the server to default to the vulnerable 2024-11-05 handler).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-11719
- https://github.com/googleapis/mcp-toolbox/pull/3049
- https://github.com/googleapis/mcp-toolbox/pull/3335
- https://github.com/googleapis/mcp-toolbox
