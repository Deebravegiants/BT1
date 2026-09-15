# [C] Dokploy: Authenticated OS command injection in backup.restoreBackupWithLogs (databaseName) leading to host RCE

## Summary
Severity: Critical
Advisory: CVE-2026-72869
Aliases: GHSA-f7mp-9jfp-mjrr
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72869
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, the backup.restoreBackupWithLogs tRPC subscription passes the databaseName parameter to restore builders in packages/server/src/utils/restore/utils.ts, where PostgreSQL, MariaDB, MySQL, and MongoDB commands embed the value in nested shell text executed by Node.js exec. An authenticated user with backup:restore permission can supply a crafted databaseName that the host /bin/sh expands before docker exec, resulting in arbitrary commands running in the Docker-privileged host context. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72869.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-f7mp-9jfp-mjrr
- https://nvd.nist.gov/vuln/detail/CVE-2026-72869
- https://github.com/Dokploy/dokploy/commit/ccd2e83c57d99f725220d37e0152270e0827d71b
- https://github.com/Dokploy/dokploy/pull/4862
