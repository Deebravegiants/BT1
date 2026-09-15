# [H] Path Traversal in googleapis/mcp-toolbox HTTP Tool URL Builder

## Summary
Severity: High
Advisory: CVE-2026-11720
Aliases: GHSA-vwxw-jrg6-9jxv, GO-2026-6411
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-11720
Type: osv

## Details
A path traversal vulnerability exists in the HTTP tool URL builder of googleapis/mcp-toolbox.

When constructing downstream API requests, the URL builder substitutes user-controlled pathParams into the configured tool path and parses the resulting string as a relative URL. While it checks that the input does not alter the scheme, host, or user info, it relies on ResolveReference for the final URL resolution. Because dot segments (../) are normalized during this resolution step, an attacker can supply path parameters containing directory traversal sequences to escape the operator-configured path scope. This allows the client to coerce the toolbox into making requests to unintended endpoints on the same target host while forwarding the toolbox's configured credentials (e.g., bypassing a restricted path like /api/v1/users/{{.id}} to reach /admin/secrets).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11720.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11720
- https://github.com/googleapis/mcp-toolbox/pull/3218
