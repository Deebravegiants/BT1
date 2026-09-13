# [H] Dokploy: Invitation Role Escalation Allows Organization Takeover

## Summary
Severity: High
Advisory: CVE-2026-45790
Aliases: GHSA-fm9p-wmpw-gxjh
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-45790
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.6, Dokploy's organization.inviteMember tRPC procedure in apps/dokploy/server/api/routers/organization.ts allows a user with member:create permission to invite an account with the owner role, while packages/server/src/services/user.ts allows a privileged self-hosted user to create an account with an arbitrary role, enabling permanent organization takeover because owner roles cannot be demoted. This issue is fixed in version 0.29.6.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45790.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-fm9p-wmpw-gxjh
- https://nvd.nist.gov/vuln/detail/CVE-2026-45790
- https://github.com/Dokploy/dokploy/commit/a07106d649991ea09892220873ea3243766c3e08
- https://github.com/Dokploy/dokploy/pull/4475
