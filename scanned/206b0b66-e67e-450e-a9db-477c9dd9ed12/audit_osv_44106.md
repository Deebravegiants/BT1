# [C] MCPHub: Authenticated non-admin user achieves RCE via POST /api/servers (missing authorization on stdio command/args)

## Summary
Severity: Critical
Advisory: CVE-2026-79748
Aliases: GHSA-mx89-jjx9-gjr8
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-79748
Type: osv

## Details
MCPHub is a unified hub for centrally managing and dynamically orchestrating multiple MCP servers/APIs into separate endpoints with flexible routing strategies. Prior to version 0.12.15, the POST /api/servers and PUT /api/servers/:name endpoints in MCPHub create/update MCP server configurations and then immediately spawn the configured stdio process via child_process.spawn. Authentication is required, but there is no authorization check restricting these endpoints to admins, and there is no allowlist/sanitization on the command and args fields. As a result, any authenticated non-admin user can submit a server configuration with command:"/bin/sh" (or any other binary) and arbitrary args, causing MCPHub to execute the attacker-controlled process as the MCPHub server's OS user (commonly root in the published Docker image and in npx/systemd deployments). This issue has been patched in version 0.12.15.

## References
- https://github.com/samanhappy/mcphub/releases/tag/v0.12.15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79748.json
- https://github.com/samanhappy/mcphub/security/advisories/GHSA-mx89-jjx9-gjr8
- https://nvd.nist.gov/vuln/detail/CVE-2026-79748
- https://github.com/samanhappy/mcphub/pull/770
