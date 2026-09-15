# [C] baserCMS < 5.3.0 SQL Injection and Code Injection via BcDatabaseService.php

## Summary
Severity: Critical
Advisory: CVE-2026-76635
Aliases: GHSA-cg65-f2m7-9fqj
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-76635
Type: osv

## Details
baserCMS before 5.3.0 contains a SQL injection vulnerability in BcDatabaseService.php that allows authenticated administrators to inject attacker-controlled table names and configuration values directly into SQL statements across sequence update, CSV export, and table management operations. Attackers can chain a backup restore code injection flaw, where PHP code outside class definitions in schema files executes unconditionally upon loading, to plant malicious table names and trigger error-based SQL injection that retrieves database version, schema contents, and arbitrary data from the PostgreSQL backend.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76635.json
- https://github.com/baserproject/basercms/releases/tag/5.3.0
- https://github.com/baserproject/basercms/security/advisories/GHSA-cg65-f2m7-9fqj
- https://nvd.nist.gov/vuln/detail/CVE-2026-76635
- https://www.vulncheck.com/advisories/basercms-sql-injection-and-code-injection-via-bcdatabaseservice-php
- https://github.com/baserproject/basercms
