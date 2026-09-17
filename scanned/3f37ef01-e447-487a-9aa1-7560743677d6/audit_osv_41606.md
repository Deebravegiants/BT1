# [H] Microsoft UFO: DNS Rebinding → Unauthenticated File Read / Command Execution

## Summary
Severity: High
Advisory: CVE-2026-62316
Aliases: GHSA-vf4c-mf32-gf2h
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-62316
Type: osv

## Details
Microsoft UFO open-source framework for intelligent automation across devices and platforms. Prior to 3.0.8, ufo/client/mcp/http_servers/linux_mcp_server.py binds a FastMCP streamable HTTP server to localhost:8010 but does not validate the Host, Origin, or Sec-Fetch-Site headers. An attacker-controlled web page can use DNS rebinding to reach the local /mcp endpoint, enumerate tool schemas through tools/list, and invoke execute_command with a valid UFO_MCP_API_KEY to read files or execute allowed operating system commands as the victim's user. This issue is fixed in version 3.0.8.

## References
- https://github.com/microsoft/UFO/releases/tag/v3.0.8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62316.json
- https://github.com/microsoft/UFO/security/advisories/GHSA-vf4c-mf32-gf2h
- https://nvd.nist.gov/vuln/detail/CVE-2026-62316
- https://github.com/microsoft/UFO/commit/3851c5d4e17c2865c56a94a6530692bf6e7a9b02
