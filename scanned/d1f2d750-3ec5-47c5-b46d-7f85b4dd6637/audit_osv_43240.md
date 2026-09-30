# [H] Dokploy: WebSocket Terminal Missing Service-Level Access Control

## Summary
Severity: High
Advisory: CVE-2026-72883
Aliases: GHSA-qf9j-c9p4-r4xp
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72883
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, the WebSocket handlers in apps/dokploy/server/wss/terminal.ts, apps/dokploy/server/wss/docker-container-terminal.ts, apps/dokploy/server/wss/docker-container-logs.ts, and apps/dokploy/server/wss/docker-stats.ts validate organization membership but do not enforce checkServiceAccess, accessedServerIds, or accessedServices, allowing an authenticated organization member to obtain root terminal access and read logs or statistics for restricted servers and services. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72883.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-qf9j-c9p4-r4xp
- https://nvd.nist.gov/vuln/detail/CVE-2026-72883
- https://github.com/Dokploy/dokploy/commit/1bc76e9e5b8a9acd14a58cd8a1828c25918f162e
- https://github.com/Dokploy/dokploy/commit/68f5afae42fca353dcb3d3bc6219ffe9e168cb91
- https://github.com/Dokploy/dokploy/pull/4865
