# [C] MCP Inspector proxy server lacks authentication between the Inspector client and proxy

## Summary
Severity: Critical
Advisory: GHSA-7f8r-222p-6f5g
CVE: CVE-2025-49596
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-06-13
Source: https://github.com/advisories/GHSA-7f8r-222p-6f5g
Type: github-advisory

## Affected
- npm: `@modelcontextprotocol/inspector` — affected >=0 <0.14.1

## Details
Versions of MCP Inspector below 0.14.1 are vulnerable to remote code execution due to lack of authentication between the Inspector client and proxy, allowing unauthenticated requests to launch MCP commands over stdio. Users should immediately upgrade to version 0.14.1 or later to address these vulnerabilities.

Credit: Rémy Marot <bughunters@tenable.com>

## References
- https://github.com/modelcontextprotocol/inspector/security/advisories/GHSA-7f8r-222p-6f5g
- https://nvd.nist.gov/vuln/detail/CVE-2025-49596
- https://github.com/modelcontextprotocol/inspector/commit/50df0e1ec488f3983740b4d28d2a968f12eb8979
- https://github.com/modelcontextprotocol/inspector
- https://thenewstack.io/mcp-vulnerability-exposes-the-ai-untrusted-code-crisis
- https://www.oligo.security/blog/critical-rce-vulnerability-in-anthropic-mcp-inspector-cve-2025-49596
