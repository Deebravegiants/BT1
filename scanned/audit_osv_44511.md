# [M] PostgreSQL Anonymizer: Privilege escalation to superuser via anon.anonymize_database_parallel()

## Summary
Severity: Medium
Advisory: CVE-2026-83534
CVSS: 6.4 (CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-09-06
Source: https://osv.dev/vulnerability/CVE-2026-83534
Type: osv

## Details
PostgreSQL Anonymizer contains a vulnerability in the anon.anonymize_database_parallel() function that allows the owner of a table to run arbitrary code with superuser privilege. The issue is fixed in PostgreSQL Anonymizer 3.2.0 and later versions

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/83xxx/CVE-2026-83534.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-83534
- https://gitlab.com/dalibo/postgresql_anonymizer/-/issues/666
