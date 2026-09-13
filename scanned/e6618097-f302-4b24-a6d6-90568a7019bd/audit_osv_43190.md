# [H] Dokploy: Cross-organization authorization bypass in server.remove allows deletion of another organization's server registration

## Summary
Severity: High
Advisory: CVE-2026-72734
Aliases: GHSA-3rpx-c3j9-q99x
CVSS: 8.4 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72734
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). From 0.28.7 until 0.29.13, the server.remove tRPC mutation in apps/dokploy/server/api/routers/server.ts accepts a caller-controlled serverId and calls haveActiveServices, findServerById, removeDeploymentsByServerId, and deleteServer without verifying that currentServer.organizationId equals ctx.session.activeOrganizationId. An authenticated owner or administrator with server:delete in one organization who previously observed another organization's serverId can delete that organization's server registration and deployment records, interrupt Dokploy management, and receive the associated plaintext SSH private key even though server.one denies the same cross-organization read. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72734.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-3rpx-c3j9-q99x
- https://nvd.nist.gov/vuln/detail/CVE-2026-72734
- https://github.com/Dokploy/dokploy/commit/4aee66b2d1dc2c027749a541e553aa49947075c1
- https://github.com/Dokploy/dokploy/pull/4874
