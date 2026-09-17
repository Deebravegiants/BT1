# [M] FrontAccounting < 2.4.20 SQL Injection via rep601.php

## Summary
Severity: Medium
Advisory: CVE-2026-40522
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-40522
Type: osv

## Details
FrontAccounting before 2.4.20 contains a SQL injection vulnerability in the Bank Statement report handler that allows authenticated attackers to extract arbitrary database data by injecting UNION SELECT payloads into the PARAM_0 POST parameter. Attackers can supply malicious SQL syntax through the unparameterized WHERE clause to retrieve sensitive information including usernames, password hashes, and email addresses from the users table, rendered into PDF report output.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40522.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40522
- https://sourceforge.net/p/frontaccounting/news/2026/04/release-2420/
- https://www.vulncheck.com/advisories/frontaccounting-sql-injection-via-rep601-php
- https://github.com/FrontAccountingERP/FA/commit/894adaf71393e0ef6a04fe6036fcd2464050f590
- https://jivasecurity.com/writeups/frontaccounting-sqli-bank-statement-report-cve-2026-40522
