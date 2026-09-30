# [H] OpenClaw 2026.5.20 < 2026.6.6 Authorization Bypass via MCP loopback

## Summary
Severity: High
Advisory: CVE-2026-62195
Aliases: GHSA-52xj-c9p8-78cv
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-62195
Type: osv

## Details
OpenClaw versions 2026.5.20 before 2026.6.6 contain an authorization bypass vulnerability in the MCP loopback feature that allows lower-trust callers to execute owner-only tools. Attackers can bypass authorization checks through configured input paths to execute or persist actions beyond their intended permissions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62195.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-52xj-c9p8-78cv
- https://nvd.nist.gov/vuln/detail/CVE-2026-62195
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-via-mcp-loopback
- https://github.com/openclaw/openclaw
