# [M] Dokploy: Cross-tenant Git provider secrets are disclosed to low-privileged service readers via `application.one`

## Summary
Severity: Medium
Advisory: CVE-2026-72873
Aliases: GHSA-hg9j-j5mc-phf5
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72873
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, application.one in apps/dokploy/server/api/routers/application.ts returns provider relations loaded by findApplicationById in packages/server/src/services/application.ts without redacting githubClientSecret, githubPrivateKey, or githubWebhookSecret, allowing a user with only service:read permission to retrieve another user’s Git provider secrets even when hasGitProviderAccess is false and unauthorizedProvider is set. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72873.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-hg9j-j5mc-phf5
- https://nvd.nist.gov/vuln/detail/CVE-2026-72873
- https://github.com/Dokploy/dokploy/commit/68ea9f7771afe6acca57032dc4328f93c4f25999
- https://github.com/Dokploy/dokploy/pull/4859
