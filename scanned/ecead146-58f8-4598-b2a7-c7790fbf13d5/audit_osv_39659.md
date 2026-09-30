# [C] Budibase: SCIM endpoints lack role-based authorization, BASIC users CRUD tenant users

## Summary
Severity: Critical
Advisory: CVE-2026-46425
Aliases: GHSA-q9rw-q89f-jx2f
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46425
Type: osv

## Details
Budibase is an open-source low-code platform. Prior to 3.38.2, packages/worker/src/api/routes/global/scim.ts attaches only two middlewares to the SCIM router: requireSCIM (checks the Enterprise feature flag and SCIM config) and doInScimContext (sets the SCIM request context). There is no role check. Any authenticated user who reaches the worker (BASIC role, workspace-scoped builder, anyone) can call SCIM endpoints and CRUD every user and group in the tenant. This vulnerability is fixed in 3.38.2.

## References
- https://github.com/Budibase/budibase/releases/tag/3.38.2
- https://github.com/Budibase/budibase/security/advisories/GHSA-q9rw-q89f-jx2f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46425.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46425
