# [H] WebSocket Terminal Auth Bypass

## Summary
Severity: High
Advisory: CVE-2026-72866
Aliases: GHSA-c68r-7wg9-p7v2
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72866
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, the WebSocket handler in apps/dokploy/server/wss/terminal.ts validates a session but does not authorize access to the requested server. An authenticated user can connect to /terminal?serverId=local, select the special serverId=local branch, and obtain an interactive terminal on the Dokploy host without an organization role or server-access check. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72866.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-c68r-7wg9-p7v2
- https://nvd.nist.gov/vuln/detail/CVE-2026-72866
- https://github.com/Dokploy/dokploy/commit/68f5afae42fca353dcb3d3bc6219ffe9e168cb91
- https://github.com/Dokploy/dokploy/pull/4865
