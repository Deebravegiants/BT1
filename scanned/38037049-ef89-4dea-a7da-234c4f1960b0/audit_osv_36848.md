# [C] Unauthenticated RCE in DocsGPT MCP STDIO Configuration

## Summary
Severity: Critical
Advisory: CVE-2026-26015
Aliases: GHSA-gcrq-f296-2j74
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/CVE-2026-26015
Type: osv

## Details
DocsGPT is a GPT-powered chat for documentation. From version 0.15.0 to before version 0.16.0, an attacker accessing both the official DocsGPT website or any local and public deployment, can craft a malicious payload bypassing the "MCP test" behavior to achieve arbitrary remote code execution (RCE). This issue has been patched in version 0.16.0.

## References
- https://github.com/arc53/DocsGPT/releases/tag/0.16.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26015.json
- https://github.com/arc53/DocsGPT/security/advisories/GHSA-gcrq-f296-2j74
- https://nvd.nist.gov/vuln/detail/CVE-2026-26015
- https://www.ox.security/blog/mcp-supply-chain-advisory-rce-vulnerabilities-across-the-ai-ecosystem/
- https://www.ox.security/blog/the-mother-of-all-ai-supply-chains-critical-systemic-vulnerability-at-the-core-of-the-mcp/
