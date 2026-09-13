# [M] Missing Host Header Validation in Apollo MCP Server for Localhost Deployments

## Summary
Severity: Medium
Advisory: CVE-2026-35577
Aliases: GHSA-wqrj-vp8w-f8vh
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/CVE-2026-35577
Type: osv

## Details
Apollo MCP Server is a Model Context Protocol server that exposes GraphQL operations as MCP tools. Prior to version 1.7.0, the Apollo MCP Server did not validate the Host header on incoming HTTP requests when using StreamableHTTP transport. In configurations where an HTTP-based MCP server is run on localhost without additional authentication or network-level controls, this could potentially allow a malicious website—visited by a user running the server locally—to use DNS rebinding techniques to bypass same-origin policy restrictions and issue requests to the local MCP server. If successfully exploited, this could allow an attacker to invoke tools or access resources exposed by the MCP server on behalf of the local user. This issue is limited to HTTP-based transport modes (StreamableHTTP). It does not affect servers using stdio transport. The practical risk is further reduced in deployments that use authentication, network-level access controls, or are not bound to localhost. This vulnerability is fixed in 1.7.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35577.json
- https://github.com/apollographql/apollo-mcp-server/security/advisories/GHSA-wqrj-vp8w-f8vh
- https://nvd.nist.gov/vuln/detail/CVE-2026-35577
- https://github.com/apollographql/apollo-mcp-server/pull/602
- https://github.com/apollographql/apollo-mcp-server/pull/635
