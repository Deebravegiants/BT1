# [C] Onyx: Cross-user OAuth-token leak via /api/mcp/servers* for per-user MCP servers

## Summary
Severity: Critical
Advisory: CVE-2026-71424
Aliases: GHSA-q62f-rv3h-f822
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-71424
Type: osv

## Details
Onyx is an open-source AI platform. Prior to 3.1.10, 3.2.14, and 4.0.0, Onyx's GET /api/mcp/servers and GET /api/mcp/servers/persona/{persona_id} endpoints expose another user's OAuth Authorization header because OnyxTokenStorage.set_tokens and OnyxTokenStorage.set_client_info in backend/onyx/server/features/mcp/api.py copy per-user tokens into a shared admin MCPConnectionConfig row and _db_mcp_server_to_api_mcp_server returns that row through auth_template.headers to any BASIC_ACCESS user. This issue is fixed in versions 3.1.10, 3.2.14, and 4.0.0.

## References
- https://github.com/onyx-dot-app/onyx/releases/tag/v4.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71424.json
- https://github.com/onyx-dot-app/onyx/security/advisories/GHSA-q62f-rv3h-f822
- https://nvd.nist.gov/vuln/detail/CVE-2026-71424
- https://github.com/onyx-dot-app/onyx/commit/3f3d79d1a7722fdc84a1c61c8aa830d890017e9e
- https://github.com/onyx-dot-app/onyx/commit/4001cedd0a8968723bfe95dd188914ed56777910
- https://github.com/onyx-dot-app/onyx/commit/b103937888fd5008067c2bb6eb6e5424576394f2
- https://github.com/onyx-dot-app/onyx/pull/11238
- https://github.com/onyx-dot-app/onyx/pull/11242
- https://github.com/onyx-dot-app/onyx/pull/11243
