# [H] Snipe-IT before 8.7.0 Database Wipe via Invalid Backup Archive

## Summary
Severity: High
Advisory: CVE-2026-86748
Aliases: GHSA-4cr5-3hw8-8w5f
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-86748
Type: osv

## Details
Snipe-IT versions before 8.7.0 wipe the database before validating the uploaded backup archive in the restore endpoint. Superusers uploading corrupted or invalid zip files trigger permanent data loss with no recovery path or rollback mechanism.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86748.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-4cr5-3hw8-8w5f
- https://nvd.nist.gov/vuln/detail/CVE-2026-86748
- https://www.vulncheck.com/advisories/snipe-it-before-8.7.0-database-wipe-via-invalid-backup-archive
