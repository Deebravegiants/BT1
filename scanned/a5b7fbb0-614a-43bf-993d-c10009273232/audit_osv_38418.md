# [C] OpenEMR Authenticated SQL Injection via backup.php Import Feature

## Summary
Severity: Critical
Advisory: CVE-2026-39931
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-39931
Type: osv

## Details
OpenEMR through 8.2.0 contains an authenticated SQL injection vulnerability in the backup configuration import feature that allows administrators with admin or super ACL privileges to execute arbitrary DDL and DML statements against the application database by uploading a crafted SQL file at the form_step=202 parameter in backup.php. Attackers can exploit the unfiltered shell_exec invocation of the mysql command-line client to extract credential hashes, modify access control tables, inject backdoor accounts, create persistent triggers or stored procedures, and write arbitrary files to the filesystem where MySQL FILE privileges and permissive secure_file_priv settings are configured.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39931.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-39931
- https://www.vulncheck.com/advisories/openemr-authenticated-sql-injection-via-backup-php-import-feature
- https://github.com/openemr/openemr
- https://jivasecurity.com/writeups/openemr-backup-import-arbitrary-sql-cve-2026-39931
