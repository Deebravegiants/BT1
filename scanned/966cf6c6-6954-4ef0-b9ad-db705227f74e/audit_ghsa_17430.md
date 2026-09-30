# [H] Docker MCP Plugin and Docker MCP Gateway have DNS Rebinding vulnerability when running in sse or streaming mode

## Summary
Severity: High
Advisory: GHSA-46gc-mwh4-cc5r
CVE: CVE-2025-64443
CWE: CWE-749
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:L/VI:H/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-12-03
Source: https://github.com/advisories/GHSA-46gc-mwh4-cc5r
Type: github-advisory

## Affected
- Go: `github.com/docker/mcp-gateway` — affected >=0 <0.28.0

## Details
### Impact
When ran in sse or streaming mode (--transport), the Docker MCP Gateway is vulnerable to a DNS rebinding attack. 

Vulnerability allows for Browser-Based exploitation of any MCP servers that are executing within the Docker MCP Gateway. Any tools or other features exposed by MCP servers can be manipulated by an attacker who is able to get a victim to visit a malicious website, or if a victim is served a malicious advertisement. 

The MCP Gateway is not prone to this attack when started in its default stdio mode, which does not listen on any network ports.


### Patches
Patch available in version v0.28.0

### Workarounds
Do not start the MCP gateway in sse or streaming mode (use default stdio)

## References
- https://github.com/docker/mcp-gateway/security/advisories/GHSA-46gc-mwh4-cc5r
- https://nvd.nist.gov/vuln/detail/CVE-2025-64443
- https://github.com/docker/mcp-gateway/pull/190
- https://github.com/docker/mcp-gateway/commit/6b076b2479d8d1345c50c112119c62978d46858e
- https://github.com/docker/mcp-gateway/commit/fe073985c8eb6e0c9317d2f198c07686f70ea06d
- https://github.com/docker/mcp-gateway
- https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#security-warning
