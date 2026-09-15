# [C] Dokploy: Cross-organization IDOR leads to root RCE on another tenant's server via swarm.*

## Summary
Severity: Critical
Advisory: CVE-2026-72876
Aliases: GHSA-jj6h-388v-9rwm
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72876
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, swarm.getNodes, swarm.getNodeInfo, swarm.getNodeApps, and swarm.getAppInfos in apps/dokploy/server/api/routers/swarm.ts accept another organization’s serverId without an activeOrganizationId ownership check, and getNodeInfo in packages/server/src/services/docker.ts interpolates nodeId into execAsyncRemote, allowing a caller with server:read permission to execute arbitrary commands as the configured SSH user on another tenant’s server. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72876.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-jj6h-388v-9rwm
- https://nvd.nist.gov/vuln/detail/CVE-2026-72876
- https://github.com/Dokploy/dokploy/commit/5563699f71b2058b49eebdfd66c6c3dbd92ede9c
- https://github.com/Dokploy/dokploy/pull/4858
