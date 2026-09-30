# [C] Dokploy: Non-admin member gains root on the host by bypassing the owner/admin check on server-level schedules (incomplete fix of CVE-2026-45632)

## Summary
Severity: Critical
Advisory: CVE-2026-72886
Aliases: GHSA-r89g-h7x9-phr2
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72886
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). From 0.29.2 until 0.29.13, schedule.create and schedule.update in apps/dokploy/server/api/routers/schedule.ts derive serviceId from applicationId or composeId and execute the owner/admin host-schedule gate only in the alternative branch, allowing a member with access to one application to attach its applicationId to a dokploy-server schedule and run a supplied script as root through schedule.runManually. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72886.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-r89g-h7x9-phr2
- https://nvd.nist.gov/vuln/detail/CVE-2026-72886
- https://github.com/Dokploy/dokploy/commit/1e3f10bd22c1c28a7b65a2d7ac15a0a5e47599eb
- https://github.com/Dokploy/dokploy/pull/4869
