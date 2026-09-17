# [H] Adminer before 5.4.3 Arbitrary File Deletion via SQLite Drop

## Summary
Severity: High
Advisory: CVE-2026-34968
Aliases: GHSA-6pg3-chwq-wgqc
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-34968
Type: osv

## Details
Adminer before 5.4.3 contains an arbitrary file deletion vulnerability in SQLite mode where the database-list drop action fails to validate file extensions before deletion. An authenticated attacker can submit arbitrary relative file paths in the db[] parameter to delete any files writable by the PHP process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34968.json
- https://github.com/vrana/adminer/security/advisories/GHSA-6pg3-chwq-wgqc
- https://nvd.nist.gov/vuln/detail/CVE-2026-34968
- https://www.vulncheck.com/advisories/adminer-before-arbitrary-file-deletion-via-sqlite-drop
