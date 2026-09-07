# [C] Dolibarr SQL injection vulnerability in admin/menus/edit.php

## Summary
Severity: Critical
Advisory: GHSA-qm8m-7626-762h
CVE: CVE-2017-14238
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qm8m-7626-762h
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <6.0.1

## Details
SQL injection vulnerability in admin/menus/edit.php in Dolibarr ERP/CRM version 6.0.0 allows remote attackers to execute arbitrary SQL commands via the menuId parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-14238
- https://github.com/Dolibarr/dolibarr/commit/d26b2a694de30f95e46ea54ea72cc54f0d38e548
- https://github.com/Dolibarr/dolibarr
