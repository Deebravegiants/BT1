# [M] CVE-2025-66689

## Summary
Severity: Medium
Advisory: CVE-2025-66689
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/CVE-2025-66689
Type: osv

## Details
A path traversal vulnerability exists in Zen MCP Server before 9.8.2 that allows authenticated attackers to read arbitrary files on the system. The vulnerability is caused by flawed logic in the is_dangerous_path() validation function that uses exact string matching against a blacklist of system directories. Attackers can bypass these restrictions by accessing subdirectories of blacklisted paths.

## References
- https://github.com/Team-Off-course/MCP-Server-Vuln-Analysis/blob/main/CVE-2025-66689.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66689.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-66689
- https://github.com/BeehiveInnovations/zen-mcp-server/issues/293
