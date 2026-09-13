# [M] LibreChat's MCP Server Header Injection Enables OAuth Token Theft

## Summary
Severity: Medium
Advisory: CVE-2026-31951
Aliases: GHSA-pmw7-gqwj-f954
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-31951
Type: osv

## Details
LibreChat is a ChatGPT clone with additional features. In versions 0.8.2-rc1 through 0.8.3-rc1, user-created MCP (Model Context Protocol) servers can include arbitrary HTTP headers that undergo credential placeholder substitution. An attacker can create a malicious MCP server with headers containing `{{LIBRECHAT_OPENID_ACCESS_TOKEN}}` (and others), causing victims who call tools on that server to have their OAuth tokens exfiltrated. Version 0.8.3-rc2 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31951.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-pmw7-gqwj-f954
- https://nvd.nist.gov/vuln/detail/CVE-2026-31951
