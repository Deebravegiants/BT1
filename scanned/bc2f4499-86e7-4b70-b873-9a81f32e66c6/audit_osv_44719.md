# [C] excel-mcp-server 0.1.8 Arbitrary File Read/Write via stdio mode

## Summary
Severity: Critical
Advisory: CVE-2026-85661
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85661
Type: osv

## Details
excel-mcp-server 0.1.8 fails to enforce path confinement in stdio mode when EXCEL_FILES_PATH is unset, allowing attackers to read and write arbitrary files. Attackers can supply unchecked file paths to read and write tools to access any file accessible to the process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85661.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85661
- https://www.vulncheck.com/advisories/excel-mcp-server-0.1.8-arbitrary-file-read-write-via-stdio-mode
- https://github.com/haris-musa/excel-mcp-server/issues/149
- https://github.com/haris-musa/excel-mcp-server
- https://github.com/haris-musa/excel-mcp-server/blob/v0.1.8/src/excel_mcp/server.py
- https://github.com/haris-musa/excel-mcp-server/blob/v0.1.8/src/excel_mcp/validation.py
