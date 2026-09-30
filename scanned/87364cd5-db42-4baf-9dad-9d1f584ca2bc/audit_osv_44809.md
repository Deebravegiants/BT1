# [H] knowns before 0.30.0 Path Traversal via code.replace MCP action

## Summary
Severity: High
Advisory: CVE-2026-86541
Aliases: GHSA-f539-xgc6-xw7q
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-07
Source: https://osv.dev/vulnerability/CVE-2026-86541
Type: osv

## Details
knowns versions before 0.30.0 contain a path traversal vulnerability in the handleCodeReplace() function that allows attackers to overwrite arbitrary files outside the project root. Attackers can supply absolute paths or relative paths containing directory traversal sequences to write malicious content to sensitive files like shell startup scripts or SSH configuration files.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86541.json
- https://github.com/knowns-dev/knowns/releases/tag/v0.30.0
- https://github.com/knowns-dev/knowns/security/advisories/GHSA-f539-xgc6-xw7q
- https://nvd.nist.gov/vuln/detail/CVE-2026-86541
- https://www.vulncheck.com/advisories/knowns-before-0.30.0-path-traversal-via-code-replace-mcp-action
- https://github.com/knowns-dev/knowns/commit/a2c98fc5c313463576c9348beeec6a74ddd7333b
- https://github.com/knowns-dev/knowns/blob/v0.29.1/internal/mcp/handlers/code.go#L588-L646
