# [M] Fetch MCP Server has a Server-Side Request Forgery (SSRF) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8fxj-2g9q-8fjw
CVE: CVE-2025-65513
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-8fxj-2g9q-8fjw
Type: github-advisory

## Affected
- npm: `mcp-fetch-server` — affected >=0

## Details
fetch-mcp v1.0.2 and before is vulnerable to Server-Side Request Forgery (SSRF) vulnerability, which allows attackers to bypass private IP validation and access internal network resources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-65513
- https://github.com/Team-Off-course/MCP-Server-Vuln-Analysis/blob/main/CVE-2025-65513.md
- https://github.com/zcaceres/fetch-mcp
- https://github.com/zcaceres/fetch-mcp/blob/c662c8ac300f715e414a64766cd95cc9ec60a1b3/src/Fetcher.ts#L20
- https://thorn-pheasant-6d8.notion.site/fetch-mcp-2853daf7b44180029ca5d56e03195736
