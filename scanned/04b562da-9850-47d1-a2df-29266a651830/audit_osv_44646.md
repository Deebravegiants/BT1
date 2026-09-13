# [M] Worklenz before 3.0.0 Authorization Bypass on Task-Scoped Endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-85389
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85389
Type: osv

## Details
Worklenz before 3.0.0 fails to verify task ownership by organization when resolving task-scoped API endpoints, allowing authenticated users to access another tenant's task data. Attackers can query task endpoints with arbitrary task UUIDs to retrieve work logs, comments, attachments, and project insights belonging to other organizations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85389.json
- https://github.com/Worklenz/worklenz/releases/tag/v3.0.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-85389
- https://www.vulncheck.com/advisories/worklenz-before-3.0.0-authorization-bypass-on-task-scoped-endpoints
- https://github.com/Worklenz/worklenz/issues/396
- https://github.com/Worklenz/worklenz/commit/f088ad0e36a23bb52857b46b3d4ce2533daeb65f
- https://github.com/Worklenz/worklenz
- https://github.com/Worklenz/worklenz/blob/v3.0.0/worklenz-backend/src/middlewares/verify-task-access.ts
