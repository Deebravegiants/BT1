# [H] MCPHub: Server-scoped bearer key gains access to an entire group via partial (any-overlap) server matching

## Summary
Severity: High
Advisory: CVE-2026-79746
Aliases: GHSA-454m-4vm6-842f
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-79746
Type: osv

## Details
MCPHub is a unified hub for centrally managing and dynamically orchestrating multiple MCP servers/APIs into separate endpoints with flexible routing strategies. Prior to version 1.0.31, when a bearer key with accessType: 'servers' (or 'custom') is used against a group route, isBearerKeyAllowedForRequest grants access to the entire group as long as any single server in that group appears in the key's allowedServers list — not only when every server the key is scoped to matches, and critically, without ever re-checking allowedServers again once the group-level connection is authorized. A key explicitly scoped to one specific server therefore also grants full access to every other server that happens to share a group with it, including servers the key was never authorized for. This issue has been patched in version 1.0.31.

## References
- https://github.com/samanhappy/mcphub/releases/tag/v1.0.31
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79746.json
- https://github.com/samanhappy/mcphub/security/advisories/GHSA-454m-4vm6-842f
- https://nvd.nist.gov/vuln/detail/CVE-2026-79746
- https://github.com/samanhappy/mcphub/commit/2b10ae36112ce68deebf910b22505d44efcef552
- https://github.com/samanhappy/mcphub/pull/1059
