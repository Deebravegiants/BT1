# [C] Dolibarr SQL injection vulnerability in comm/multiprix.php

## Summary
Severity: Critical
Advisory: GHSA-9v7m-f3cv-68rw
CVE: CVE-2017-17897
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-9v7m-f3cv-68rw
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <6.0.5

## Details
SQL injection vulnerability in comm/multiprix.php in Dolibarr ERP/CRM version 6.0.4 allows remote attackers to execute arbitrary SQL commands via the id parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-17897
- https://github.com/Dolibarr/dolibarr/commit/4a5988accbb770b74105baacd5a034689272128c
- https://github.com/Dolibarr/dolibarr
