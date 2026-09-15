# [C] ArcadeDB before 26.7.3 Authentication Bypass via MCP Transport

## Summary
Severity: Critical
Advisory: CVE-2026-68578
Aliases: GHSA-6x73-v3rc-f57c
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-02
Source: https://osv.dev/vulnerability/CVE-2026-68578
Type: osv

## Details
ArcadeDB versions before 26.7.3 fail to bind the authenticated principal in the MCP HTTP transport, causing all engine permission checks to silently pass as no-ops. Non-root MCP-allowed users can perform arbitrary database writes, DDL, schema mutations, and execute arbitrary JavaScript code via the query tool.

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-6x73-v3rc-f57c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68578.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68578
- https://www.vulncheck.com/advisories/arcadedb-authentication-bypass-via-mcp-transport
