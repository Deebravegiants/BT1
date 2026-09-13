# [M] CKAN MCP Server: Cache-key canonicalization collision enables cache confusion / poisoning

## Summary
Severity: Medium
Advisory: CVE-2026-73846
Aliases: GHSA-78x9-fhhx-v2g6
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-73846
Type: osv

## Details
CKAN MCP Server is a tool for querying CKAN open data portals. Prior to 0.4.112, canonicalizeParams in src/utils/cache.ts serializes request parameters with unescaped ampersand, equals-sign, and vertical-bar delimiters, allowing different logical parameter sets used by buildCacheKey to collide and an attacker to prime a shared cache with a response for a victim's distinct query. This issue is fixed in version 0.4.112.

## References
- https://github.com/ondata/ckan-mcp-server/releases/tag/v0.4.112
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73846.json
- https://github.com/ondata/ckan-mcp-server/security/advisories/GHSA-78x9-fhhx-v2g6
- https://nvd.nist.gov/vuln/detail/CVE-2026-73846
- https://github.com/ondata/ckan-mcp-server/commit/8e1522f9bbfa1f3b21550f17887f60f133e24151
