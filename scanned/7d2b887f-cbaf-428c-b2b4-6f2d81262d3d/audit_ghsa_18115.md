# [M] HackMD MCP Server has Server-Side Request Forgery (SSRF) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g5cg-6c7v-mmpw
CVE: CVE-2025-59155
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-g5cg-6c7v-mmpw
Type: github-advisory

## Affected
- npm: `hackmd-mcp` — affected >=1.4.0 <1.5.0

## Details
### Impact

A Server-Side Request Forgery (SSRF) vulnerability that affects all users running the HackMD MCP server in HTTP mode. Attackers could exploit this vulnerability by passing arbitrary `hackmdApiUrl` values through HTTP headers (`Hackmd-Api-Url`) or base64-encoded JSON query parameters. This allows malicious users to:

- Redirect API calls to internal network services
- Potentially access sensitive internal endpoints
- Perform network reconnaissance through the server
- Bypass network access controls

The vulnerability affects the HTTP transport mode specifically - stdio mode is not impacted as it only accepts requests from stdio.

### Patches

The vulnerability has been patched in version `1.5.0`. Users should:

1. Update to the latest version of the HackMD MCP server
2. Set the `ALLOWED_HACKMD_API_URLS` environment variable to restrict allowed HackMD API endpoints
3. If not set, the server will default to only allowing the official HackMD API URL (`https://api.hackmd.io/v1`)

Example configuration:
```
ALLOWED_HACKMD_API_URLS=https://api.hackmd.io/v1,https://your-hackmd-instance.com/api/v1
```

### Workarounds

Users can mitigate this vulnerability without upgrading by:

1. **Use stdio mode instead of HTTP mode**: Set `TRANSPORT=stdio` or remove the `TRANSPORT` environment variable to disable HTTP mode entirely
2. **Network-level restrictions**: Use firewall rules or network policies to restrict outbound connections from the server
3. **Reverse proxy filtering**: Place the MCP server behind a reverse proxy that validates and filters both the `Hackmd-Api-Url` header and the base64-encoded JSON `config` query parameter to prevent malicious `hackmdApiUrl` values

### References

- [OWASP Server-Side Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [HackMD MCP Server Documentation](https://github.com/yuna0x0/hackmd-mcp)

## References
- https://github.com/yuna0x0/hackmd-mcp/security/advisories/GHSA-g5cg-6c7v-mmpw
- https://nvd.nist.gov/vuln/detail/CVE-2025-59155
- https://github.com/yuna0x0/hackmd-mcp/commit/43936c78a5bb3dedc74e8f080607a1125caa8c13
- https://github.com/yuna0x0/hackmd-mcp
- https://github.com/yuna0x0/hackmd-mcp/releases/tag/v1.5.0
