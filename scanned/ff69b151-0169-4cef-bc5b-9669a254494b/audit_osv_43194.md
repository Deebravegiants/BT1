# [C] Dokploy: Authenticated RCE via Command Injection in backup.listBackupFiles search Parameter

## Summary
Severity: Critical
Advisory: CVE-2026-72738
Aliases: GHSA-5vjv-73wr-rf79
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72738
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, the backup.listBackupFiles tRPC endpoint in apps/dokploy/server/api/routers/backup.ts passes the search parameter through normalizeS3Path and interpolates it into an rclone lsjson command executed by child_process.exec(), allowing an authenticated user with backup:read permission to execute arbitrary commands on the Dokploy host. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72738.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-5vjv-73wr-rf79
- https://nvd.nist.gov/vuln/detail/CVE-2026-72738
- https://github.com/Dokploy/dokploy/commit/eeb6e7b8ea88e4b4b1fac8460755464100516ac9
