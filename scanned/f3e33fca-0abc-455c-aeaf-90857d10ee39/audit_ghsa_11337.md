# [H] Azure MCP Server has Server-Side Request Forgery issue that allows authorized attacker to elevate privileges over a network

## Summary
Severity: High
Advisory: GHSA-hhfx-wfvq-7g9c
CVE: CVE-2026-26118
CWE: CWE-918
Ecosystem: NuGet, PyPI, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-hhfx-wfvq-7g9c
Type: github-advisory

## Affected
- NuGet: `Azure.Mcp` — affected >=2.0.0-beta.1 <2.0.0-beta.17
- NuGet: `Azure.Mcp` — affected >=1.0.0 <1.0.2
- npm: `@azure/mcp` — affected >=2.0.0-beta.1 <2.0.0-beta.17
- PyPI: `msmcp-azure` — affected >=2.0.0b14 <2.0.0b17
- npm: `@azure/mcp` — affected >=1.0.0 <1.0.2

## Details
Server-Side Request Forgery (SSRF) in Azure MCP Server allows an authorized attacker to elevate privileges over a network.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-26118
- https://github.com/microsoft/mcp/commit/804ff60293206c4d8e832f772097238561bf2c34
- https://github.com/microsoft/mcp
- https://github.com/microsoft/mcp/releases/tag/Azure.Mcp.Server-1.0.2
- https://github.com/microsoft/mcp/releases/tag/Azure.Mcp.Server-2.0.0-beta.17
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2026-26118
