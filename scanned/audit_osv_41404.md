# [M] SiYuan before v3.8.0 Incomplete Path Blocklist via MCP file tool

## Summary
Severity: Medium
Advisory: CVE-2026-60083
Aliases: GHSA-c8r8-95hg-mp34
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-60083
Type: osv

## Details
SiYuan versions before v3.8.0 contain an incomplete path blocklist in the MCP file tool that fails to restrict access to sensitive workspace files protected by the HTTP API. Authenticated administrators can read plaintext publish-mode passwords from data/.siyuan/publishAccess.json and access other sensitive files like data/templates and data/snippets/conf.json.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/60xxx/CVE-2026-60083.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-c8r8-95hg-mp34
- https://nvd.nist.gov/vuln/detail/CVE-2026-60083
- https://www.vulncheck.com/advisories/siyuan-before-incomplete-path-blocklist-via-mcp-file-tool
