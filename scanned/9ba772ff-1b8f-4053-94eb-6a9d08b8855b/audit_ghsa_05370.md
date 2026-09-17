# [H] Microsoft Playwright MCP Server vulnerable to DNS Rebinding Attack; Allows Attackers Access to All Server Tools

## Summary
Severity: High
Advisory: GHSA-6fg3-hvw7-2fwq
CVE: CVE-2025-9611
CWE: CWE-749
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:L/VA:H/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2026-01-07
Source: https://github.com/advisories/GHSA-6fg3-hvw7-2fwq
Type: github-advisory

## Affected
- npm: `@playwright/mcp` — affected >=0 <0.0.40

## Details
Microsoft Playwright MCP Server versions prior to 0.0.40 fails to validate the Origin header on incoming connections. This allows an attacker to perform a DNS rebinding attack via a victim’s web browser and send unauthorized requests to a locally running MCP server, resulting in unintended invocation of MCP tool endpoints.

## References
- https://github.com/JLLeitschuh/security-research/security/advisories/GHSA-8rgw-6xp9-2fg3
- https://nvd.nist.gov/vuln/detail/CVE-2025-9611
- https://github.com/microsoft/playwright-mcp/issues/1206
- https://github.com/microsoft/playwright/commit/1313fbd
- https://github.com/microsoft/playwright-mcp
- https://msrc.microsoft.com/report/vulnerability/VULN-164412
- https://www.vulncheck.com/advisories/microsoft-playwright-mcp-server-dns-rebinding-via-missing-origin-header-validation
