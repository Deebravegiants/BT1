# [C] Nhost CLI MCP Server: Missing Inbound Authentication on Explicitly Bound Network Port

## Summary
Severity: Critical
Advisory: CVE-2026-34200
Aliases: GHSA-6c5x-3h35-vvw2
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34200
Type: osv

## Details
Nhost is an open source Firebase alternative with GraphQL. Prior to version 1.41.0, The Nhost CLI MCP server, when explicitly configured to listen on a network port, applies no inbound authentication and does not enforce strict CORS. This allows a malicious website visited on the same machine to issue cross-origin requests to the MCP server and invoke privileged tools using the developer's locally configured credentials. This vulnerability requires two explicit, non-default configuration steps to be exploitable. The default nhost mcp start configuration is not affected. This issue has been patched in version 1.41.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34200.json
- https://github.com/nhost/nhost/security/advisories/GHSA-6c5x-3h35-vvw2
- https://nvd.nist.gov/vuln/detail/CVE-2026-34200
- https://github.com/nhost/nhost/commit/15eae9285f9dce63e184b9bb24616474ffa5ccc9
- https://github.com/nhost/nhost/pull/4060
