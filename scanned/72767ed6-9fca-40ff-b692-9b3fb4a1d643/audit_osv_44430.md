# [H] HyperDX Team Management Operations Missing Role-Based Access Control

## Summary
Severity: High
Advisory: CVE-2026-82279
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82279
Type: osv

## Details
HyperDX through 1.10.1 fails to enforce role-based access controls in team management endpoints, allowing any team member to perform administrative actions. Attackers can delete team members including owners, rotate API keys, and rename teams by sending requests to PATCH /team/apiKey, PATCH /team/name, and DELETE /team/member endpoints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82279.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82279
- https://www.vulncheck.com/advisories/hyperdx-team-management-operations-missing-role-based-access-control
- https://github.com/hyperdxio/hyperdx/issues/2587
- https://github.com/hyperdxio/hyperdx
- https://github.com/hyperdxio/hyperdx/blob/db6ee45feadb2e229bb234364b8661903f8e386e/packages/api/src/routers/api/team.ts
