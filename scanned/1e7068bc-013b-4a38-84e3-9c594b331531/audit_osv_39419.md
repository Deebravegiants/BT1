# [C] Dokploy: Schedule Authorization Bypass Enables Host/Server Command Execution

## Summary
Severity: Critical
Advisory: CVE-2026-45632
Aliases: GHSA-7wmr-57mg-h5q6
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-45632
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). In 0.26.7 and earlier, the schedule router does not enforce organization/role checks. As a result, any authenticated user can create, update, run, or delete schedules belonging to other organizations if they know the scheduleId/serverId. Schedule types server and dokploy-server write and execute scripts on the host or remote servers, enabling RCE on the Dokploy host or a target server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45632.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-7wmr-57mg-h5q6
- https://nvd.nist.gov/vuln/detail/CVE-2026-45632
