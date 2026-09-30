# [C] Wolf CMS 0.8.3.1 Authorization Bypass via BackupRestoreController

## Summary
Severity: Critical
Advisory: CVE-2026-67207
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-67207
Type: osv

## Details
Wolf CMS through 0.8.3.1 contains an authorization bypass vulnerability in BackupRestoreController that allows authenticated non-administrative users to access restricted backup functionality due to a PHP operator precedence flaw in the permission check expression. Attackers can exploit the incorrect evaluation of the access control expression to create, download, and restore backups without administrative privileges.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67207.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67207
- https://www.vulncheck.com/advisories/wolf-cms-authorization-bypass-via-backuprestorecontroller
- https://github.com/wolfcms/wolfcms
- https://github.com/Caycon/cve-advisories/blob/main/2026/WolfCms/CVE-2026-67207.md
