# [C] marimo < 0.23.15 Code Injection via MCP Server Configuration

## Summary
Severity: Critical
Advisory: CVE-2026-75149
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-75149
Type: osv

## Details
marimo before 0.23.15 contains a code injection vulnerability in the notebook configuration handler that allows attackers to execute arbitrary commands by supplying a crafted MCP server entry with an attacker-controlled command value embedded in a notebook. When the notebook is opened in edit mode, marimo launches the specified command as a local subprocess before any notebook cell is executed, requiring no authentication or cell execution to trigger the vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75149.json
- https://github.com/marimo-team/marimo/releases/tag/0.23.15
- https://nvd.nist.gov/vuln/detail/CVE-2026-75149
- https://www.vulncheck.com/advisories/marimo-code-injection-via-mcp-server-configuration
- https://github.com/marimo-team/marimo/pull/10281
- https://github.com/marimo-team/marimo/commit/1a21bd71e258438d2511136b5edacc94c08855f4
- https://github.com/marimo-team/marimo
