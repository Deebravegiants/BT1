# [C] Dokploy: OS Command Injection via `databaseName` / `backupFile` in database restore

## Summary
Severity: Critical
Advisory: CVE-2026-72733
Aliases: GHSA-2xjq-p4xx-5x2p
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72733
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, the backup.restoreBackupWithLogs tRPC subscription builds database restore shell pipelines from the user-controlled databaseName and backupFile fields without safely separating them from shell syntax. packages/server/src/utils/restore/utils.ts interpolates databaseName into database-specific restore commands, while packages/server/src/utils/restore/postgres.ts and the analogous restore modules interpolate backupFile into rclone paths. An authenticated member with backup-restore permission can inject operating-system commands that execute in the Dokploy host context through execAsync or execAsyncRemote, even when no valid database container or backup file exists. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72733.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-2xjq-p4xx-5x2p
- https://nvd.nist.gov/vuln/detail/CVE-2026-72733
- https://github.com/Dokploy/dokploy/commit/8539a5c82f47eb3fd1464b574eb034c6dc2a6bbd
- https://github.com/Dokploy/dokploy/commit/ccd2e83c57d99f725220d37e0152270e0827d71b
- https://github.com/Dokploy/dokploy/commit/eeb6e7b8ea88e4b4b1fac8460755464100516ac9
- https://github.com/Dokploy/dokploy/pull/4862
