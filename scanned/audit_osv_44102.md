# [H] MCPHub: Missing Authorization on `PUT /api/system-config` Lets Any Non-Admin Rewrite Global Security Configuration

## Summary
Severity: High
Advisory: CVE-2026-79744
Aliases: GHSA-4gc8-885f-qj36
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-79744
Type: osv

## Details
MCPHub is a unified hub for centrally managing and dynamically orchestrating multiple MCP servers/APIs into separate endpoints with flexible routing strategies. Prior to version 1.0.29, MCPHub's PUT /api/system-config endpoint (handler updateSystemConfig) performs no authorization check. It is protected only by the app-wide authentication middleware and a rate limiter — it never inspects req.user.isAdmin. This issue has been patched in version 1.0.29.

## References
- https://github.com/samanhappy/mcphub/releases/tag/v1.0.29
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79744.json
- https://github.com/samanhappy/mcphub/security/advisories/GHSA-4gc8-885f-qj36
- https://nvd.nist.gov/vuln/detail/CVE-2026-79744
