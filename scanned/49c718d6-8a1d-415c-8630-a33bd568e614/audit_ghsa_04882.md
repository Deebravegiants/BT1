# [C] MCP Toolbox for Databases has an Origin Validation Error

## Summary
Severity: Critical
Advisory: GHSA-76g7-m3xw-x9gr
CVE: CVE-2026-11624
CWE: CWE-346
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-06-13
Source: https://github.com/advisories/GHSA-76g7-m3xw-x9gr
Type: github-advisory

## Affected
- Go: `github.com/googleapis/mcp-toolbox` — affected >=0 <0.25.0

## Details
The Model Context Protocol has a security warning advising servers to validate the "Origin" header on all incoming connections to prevent DNS rebinding attacks. Prior to the v0.25.0 release, users had no way to validate the origin's host. In v0.25.0, a new "--allowed-hosts" flag was introduced alongside the existing "--allowed-origins" flag, enabling users to specify permitted hosts at server startup. Both flags default to "*", allowing users to implement strict access controls as needed without breaking existing setups. If either flag is set to "*", the server will output a startup warning about potential vulnerabilities. Documentation has also been updated to highlight these security considerations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-11624
- https://github.com/googleapis/mcp-toolbox/issues/3113
- https://github.com/googleapis/mcp-toolbox/pull/2254
- https://github.com/googleapis/mcp-toolbox/commit/17b41f64531b8fe417c28ada45d1992ba430dc1b
- https://github.com/googleapis/mcp-toolbox
