# [H] DNS Rebinding Protection Disabled by Default in Model Context Protocol Go SDK for Servers Running on Localhost

## Summary
Severity: High
Advisory: GHSA-xw59-hvm2-8pj6
CVE: CVE-2026-34742
CWE: CWE-1188
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-xw59-hvm2-8pj6
Type: github-advisory

## Affected
- Go: `github.com/modelcontextprotocol/go-sdk` — affected >=0 <1.4.0

## Details
The Model Context Protocol (MCP) Go SDK does not enable DNS rebinding protection by default for HTTP-based servers. When an HTTP-based MCP server is run on localhost without authentication with `StreamableHTTPHandler` or `SSEHandler`, a malicious website could exploit DNS rebinding to bypass same-origin policy restrictions and send requests to the local MCP server. This could allow an attacker to invoke tools or access resources exposed by the MCP server on behalf of the user in those limited circumstances.

Note that running HTTP-based MCP servers locally without authentication is not recommended per MCP security best practices. This issue does not affect servers using stdio transport.

Servers created via `StreamableHTTPHandler` or `SSEHandler` now have this protection enabled by default when binding to `localhost`. Users are advised to update to version `1.4.0` to receive this automatic protection.

## References
- https://github.com/modelcontextprotocol/go-sdk/security/advisories/GHSA-xw59-hvm2-8pj6
- https://nvd.nist.gov/vuln/detail/CVE-2026-34742
- https://github.com/modelcontextprotocol/go-sdk/pull/760
- https://github.com/modelcontextprotocol/go-sdk/commit/67bd3f2e2b53ce11a16db8d976cdb8ff1e986b6d
- https://access.redhat.com/errata/RHSA-2026:21772
- https://access.redhat.com/security/cve/CVE-2026-34742
- https://bugzilla.redhat.com/show_bug.cgi?id=2454608
- https://github.com/modelcontextprotocol/go-sdk
- https://github.com/modelcontextprotocol/go-sdk/releases/tag/v1.4.0
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-34742.json
