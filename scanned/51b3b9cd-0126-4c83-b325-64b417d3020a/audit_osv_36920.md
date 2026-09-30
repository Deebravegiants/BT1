# [H] Free PBX backup: Deserialization of Untrusted Data in admin/modules/backup/Models/BackupSplFileInfo.php

## Summary
Severity: High
Advisory: CVE-2026-26978
Aliases: GHSA-5v7h-49gr-jcwr
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-18
Source: https://osv.dev/vulnerability/CVE-2026-26978
Type: osv

## Details
FreePBX is an open source IP PBX. In versions below 16.0.71 and 17.0.6, the backup module does not properly sanitize data during restore operations, potentially leading to compromise if the backup contains carefully crafted hostile data. During backup restore operations, FreePBX extracts selected files from a user-supplied tar archive. If a malicious file exists in the archive, it is read and passed directly to unserialize() without validation, class restrictions, or integrity checks. This issue allows Remote Code Execution during restoration of the backup as the web server user (typically asterisk or www-data). The attack does not require shell access, CLI access, or filesystem write permissions beyond the normal restore workflow. Authentication with a known username that has sufficient access permissions and/or write access to backup files is required. This issue has been fixed in versions 16.0.71 and 17.0.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26978.json
- https://github.com/FreePBX/security-reporting/security/advisories/GHSA-5v7h-49gr-jcwr
- https://nvd.nist.gov/vuln/detail/CVE-2026-26978
- https://github.com/FreePBX/backup/commit/45c57e1207cbf9fd1c5f76f8a3e72d204a69a472
- https://github.com/FreePBX/backup/commit/64781af5c80cce0cff21a981be4d8e6a7a71f2c4
