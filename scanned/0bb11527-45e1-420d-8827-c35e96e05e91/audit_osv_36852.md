# [H] sf-mcp-server has a Command Injection in query_records tool due to unsafe use of child_process.exec

## Summary
Severity: High
Advisory: CVE-2026-26029
Aliases: GHSA-h4w9-g9c5-vfwq
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-11
Source: https://osv.dev/vulnerability/CVE-2026-26029
Type: osv

## Details
sf-mcp-server is an implementation of Salesforce MCP server for Claude for Desktop. A command injection vulnerability exists in sf-mcp-server due to unsafe use of child_process.exec when constructing Salesforce CLI commands with user-controlled input. Successful exploitation allows attackers to execute arbitrary shell commands with the privileges of the MCP server process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26029.json
- https://github.com/akutishevsky/sf-mcp-server/security/advisories/GHSA-h4w9-g9c5-vfwq
- https://nvd.nist.gov/vuln/detail/CVE-2026-26029
- https://github.com/akutishevsky/sf-mcp-server/commit/99fba0171b8c22b5ee3c0405053ccfd2910a066d
