# [C] Dokploy: Remote Code Execution via volume-backup

## Summary
Severity: Critical
Advisory: CVE-2026-72901
Aliases: GHSA-w223-vw9m-4f9c
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72901
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, Dokploy allows an authenticated low-privilege member to execute arbitrary commands on the control-plane host because the volumeName field accepted by volumeBackup.create and volumeBackup.runManually is interpolated without quoting in packages/server/src/utils/volume-backups/backup.ts and executed through child_process.exec, with Docker socket access making execution host/root-equivalent. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72901.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-w223-vw9m-4f9c
- https://nvd.nist.gov/vuln/detail/CVE-2026-72901
- https://github.com/Dokploy/dokploy/commit/d629faebc6dcb9d4785f84bf30b2b285f9f59379
- https://github.com/Dokploy/dokploy/pull/4873
