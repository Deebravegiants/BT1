# [M] @aborruso/ckan-mcp-server: SSRF via base_url allows access to internal networks (Potential fix bypass of CVE-2026-33060)

## Summary
Severity: Medium
Advisory: GHSA-g84h-j7jj-x32p
CVE: CVE-2026-53509
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-g84h-j7jj-x32p
Type: github-advisory

## Affected
- npm: `@aborruso/ckan-mcp-server` — affected >=0 <0.4.106

## Details
### Summary
A known vulnerability CVE-2026-33060 indicated tools including ckan_package_search and sparql_query that accept a base_url parameter had the risk of making HTTP requests to arbitrary endpoints without restriction. A fix was applied to filter out ip addresses. However, a method to bypass exists.

### Details
CKAN MCP Server validates caller-supplied CKAN server URLs by inspecting only the parsed hostname string before issuing outbound HTTP requests. In `src/utils/http.ts`, hostname aliases such as `ip6-localhost` are not equal to `localhost`, are not dotted IPv4 literals, and are not bracketed IPv6 literals, so they pass the SSRF filter but can resolve to loopback when the server performs the request. A remote MCP caller that can invoke CKAN tools with a `server_url` can therefore make the server connect to local or private addresses and, for CKAN-shaped responses, receive response-derived data.

### Fix
Replaced the single `hostname === 'localhost'` check with a blocked-hostname `Set` covering `ip6-localhost` and `ip6-loopback`. Patched in commit `c761045a1b7c5f40d2626540dd2ef1d4feb91f8c`.

---
@aborruso/ckan-mcp-server thanks **hibrian827** for responsibly disclosing this issue.

## References
- https://github.com/ondata/ckan-mcp-server/security/advisories/GHSA-g84h-j7jj-x32p
- https://github.com/advisories/GHSA-3xm7-qw7j-qc8v
- https://github.com/ondata/ckan-mcp-server
- https://github.com/ondata/ckan-mcp-server/releases/tag/v0.4.106
