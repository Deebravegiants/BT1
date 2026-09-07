# [H] Dolibarr has SQL injection vulnerability in the rowid parameter of the admin dict.php

## Summary
Severity: High
Advisory: GHSA-xxxg-x793-7fq3
CVE: CVE-2019-25710
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-12
Source: https://github.com/advisories/GHSA-xxxg-x793-7fq3
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0

## Details
Dolibarr ERP-CRM 8.0.4 contains an SQL injection vulnerability in the rowid parameter of the admin dict.php endpoint that allows attackers to execute arbitrary SQL queries. Attackers can inject malicious SQL code through the rowid POST parameter to extract sensitive database information using error-based SQL injection techniques.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25710
- https://github.com/Dolibarr/dolibarr
- https://sourceforge.net/projects/dolibarr/files/Dolibarr%20ERP-CRM/8.0.4/dolibarr-8.0.4.zip
- https://www.dolibarr.org
- https://www.exploit-db.com/exploits/46095
- https://www.vulncheck.com/advisories/dolibarr-erp-crm-sql-injection-via-rowid-parameter
