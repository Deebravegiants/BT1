# [C] Dolibarr SQL injection vulnerability in fourn/index.php

## Summary
Severity: Critical
Advisory: GHSA-6frc-vfw9-wm27
CVE: CVE-2017-17900
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-6frc-vfw9-wm27
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <6.0.5

## Details
SQL injection vulnerability in fourn/index.php in Dolibarr ERP/CRM version 6.0.4 allows remote attackers to execute arbitrary SQL commands via the socid parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-17900
- https://github.com/Dolibarr/dolibarr/commit/4a5988accbb770b74105baacd5a034689272128c
- https://github.com/Dolibarr/dolibarr
