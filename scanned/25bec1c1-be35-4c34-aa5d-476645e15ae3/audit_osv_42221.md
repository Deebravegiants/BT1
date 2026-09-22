# [H] Office-Word-MCP-Server 1.1.11 Path Traversal via document tools

## Summary
Severity: High
Advisory: CVE-2026-65695
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-65695
Type: osv

## Details
Office-Word-MCP-Server through 1.1.11 contains a path traversal vulnerability in its document tools that allows attackers who can influence the filename argument to read arbitrary .docx files or create and overwrite .docx files outside the intended working directory. Attackers can supply absolute paths or ../ traversal sequences directly to document open and save operations, bypassing the check_file_writeable and ensure_docx_extension helpers which perform no base-directory confinement or realpath validation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65695.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65695
- https://www.vulncheck.com/advisories/office-word-mcp-server-path-traversal-via-document-tools
- https://github.com/GongRzhe/Office-Word-MCP-Server
- https://github.com/geo-chen/oss/blob/main/Office-Word-MCP-Server.md
