# [H] Telnyx MCP Server through 6.83.0 Missing Authentication on Streamable HTTP Transport

## Summary
Severity: High
Advisory: CVE-2026-81098
Aliases: GHSA-46jp-xr2h-fw7h
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81098
Type: osv

## Details
The Telnyx MCP server exposed its HTTP transport on every interface and did not require a caller credential. packages/mcp-server/src/http.ts served MCP on the root path with a listener bound to all interfaces and parsed the caller's authentication headers in a mode that did not fail when they were absent, so a request without any credential completed initialisation and dispatched tools. Dispatch forwarded the server's own stored credentials, the Telnyx API key and client secret together with the code-execution key, to the upstream endpoint, so an unauthenticated caller able to reach the port acted with them. The current code defaults the host to loopback, requires a server API key, and enforces it in middleware.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81098.json
- https://github.com/team-telnyx/telnyx-node/security/advisories/GHSA-46jp-xr2h-fw7h
- https://nvd.nist.gov/vuln/detail/CVE-2026-81098
- https://www.vulncheck.com/advisories/telnyx-mcp-server-through-6.83.0-missing-authentication-on-streamable-http-transport
- https://github.com/team-telnyx/telnyx-node/pull/450
- https://github.com/team-telnyx/telnyx-node
