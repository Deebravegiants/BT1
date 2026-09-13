# [H] n8n-mcp has unauthenticated session termination and information disclosure in HTTP transport

## Summary
Severity: High
Advisory: GHSA-75hx-xj24-mqrw
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-75hx-xj24-mqrw
Type: github-advisory

## Affected
- npm: `n8n-mcp` — affected >=0 <2.47.6

## Details
### Summary

Several HTTP transport endpoints in n8n-mcp lacked proper authentication, and the health check endpoint exposed sensitive operational metadata without credentials.

### Impact

An unauthenticated attacker with network access to the n8n-mcp HTTP server could disrupt active MCP sessions and gather information useful for further attacks.

### Patches

Fixed in **v2.47.6**. All MCP session endpoints now require Bearer authentication. The health check endpoint has been reduced to a minimal liveness response.

### Workarounds

If you cannot upgrade immediately:

- **Restrict network access** to the HTTP server using firewall rules, reverse proxy IP allowlists, or a VPN so that only trusted clients can reach it.
- **Use stdio mode** (`MCP_MODE=stdio`) instead of HTTP mode. The stdio transport does not expose any HTTP endpoints and is unaffected by this vulnerability.

Upgrading to v2.47.6 is still strongly recommended.

### Credit

Reported by @yotampe-pluto.

## References
- https://github.com/czlonkowski/n8n-mcp/security/advisories/GHSA-75hx-xj24-mqrw
- https://github.com/czlonkowski/n8n-mcp/commit/ca9d4b3df6419b8338983be98f7940400f78bde3
- https://github.com/czlonkowski/n8n-mcp
- https://github.com/czlonkowski/n8n-mcp/releases/tag/v2.47.6
