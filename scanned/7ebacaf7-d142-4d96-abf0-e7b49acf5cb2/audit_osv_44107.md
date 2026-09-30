# [H] MCPHub: SSRF Guard Bypass via IPv6 Transition Addresses in URL Validation

## Summary
Severity: High
Advisory: CVE-2026-79749
Aliases: GHSA-pr4x-3pc7-2fhw
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-79749
Type: osv

## Details
MCPHub is a unified hub for centrally managing and dynamically orchestrating multiple MCP servers/APIs into separate endpoints with flexible routing strategies. Prior to version 1.0.32, MCPHub's SSRF guard in src/utils/ssrf.ts uses a custom isBlockedIpv6 function that only checks for loopback, link-local, unique-local, IPv4-mapped, and IPv4-compatible IPv6 addresses. IPv6 transition address families -- NAT64 (64:ff9b::/96), 6to4 (2002::/16), and Teredo (2001::/32) -- are not checked. An attacker who can specify a URL for an MCP server connection can encode a private IPv4 address inside one of these IPv6 forms to bypass the SSRF guard and reach internal infrastructure. This issue has been patched in version 1.0.32.

## References
- https://github.com/samanhappy/mcphub/releases/tag/v1.0.32
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79749.json
- https://github.com/samanhappy/mcphub/security/advisories/GHSA-pr4x-3pc7-2fhw
- https://nvd.nist.gov/vuln/detail/CVE-2026-79749
- https://github.com/samanhappy/mcphub/commit/2b10ae36112ce68deebf910b22505d44efcef552
- https://github.com/samanhappy/mcphub/pull/1069
