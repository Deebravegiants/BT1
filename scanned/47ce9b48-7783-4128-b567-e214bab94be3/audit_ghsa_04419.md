# [M] NocoDB: Cross-Workspace Integration Use in Connection Test

## Summary
Severity: Medium
Advisory: GHSA-96fh-m4r8-6v9v
CVE: CVE-2026-47381
CWE: CWE-290
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-96fh-m4r8-6v9v
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <2026.05.1

## Details
### Summary
A user in one workspace could exercise another workspace's integration through the
`testConnection` endpoint by supplying its ID, because the integration was fetched in
a bypass scope and the caller's permission check matched any base in any workspace.

### Details
The connection-test endpoint fetched the integration in `RootScopes.BYPASS` scope and
checked only that the integration was non-private and that the caller held an
owner/creator role on any base in any workspace. The permission lookup is now scoped
to the integration's workspace by joining on `fk_workspace_id`, and the controller
rejects requests where the integration's workspace differs from the request's workspace.

### Impact
Cross-tenant access to integration configuration through the connection-test endpoint,
including the ability to drive the resolved database with the other workspace's
credentials. Authentication with creator-or-owner role on any base in any workspace
was sufficient.

### Credit
This issue was reported by [@DongyangLyu](https://github.com/DongyangLyu).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-96fh-m4r8-6v9v
- https://nvd.nist.gov/vuln/detail/CVE-2026-47381
- https://github.com/nocodb/nocodb
- https://github.com/nocodb/nocodb/releases/tag/2026.05.1
