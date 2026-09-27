# [H] MCPHub vulnerable to SSRF: a non-admin user can make mcphub request arbitrary URLs and read the response (OpenAPI proxy + transport dial)

## Summary
Severity: High
Advisory: CVE-2026-79747
Aliases: GHSA-9wx9-prgc-gmjr
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-79747
Type: osv

## Details
MCPHub is a unified hub for centrally managing and dynamically orchestrating multiple MCP servers/APIs into separate endpoints with flexible routing strategies. Prior to version 1.0.32, an authenticated non-admin user can register a server pointing at an arbitrary URL and make the hub issue server-side requests to it, with no egress filtering (no block of loopback / RFC1918 / link-local 169.254.0.0/16). Via the OpenAPI proxy path the response body is returned to the caller (full, reflected SSRF); via the SSE/streamable-http transport the request is sent blind. This issue has been patched in version 1.0.32.

## References
- https://github.com/samanhappy/mcphub/releases/tag/v1.0.32
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79747.json
- https://github.com/samanhappy/mcphub/security/advisories/GHSA-9wx9-prgc-gmjr
- https://nvd.nist.gov/vuln/detail/CVE-2026-79747
