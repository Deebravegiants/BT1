# [C] Dolibarr SQL injection vulnerability in don/list.php

## Summary
Severity: Critical
Advisory: GHSA-jjgq-jq8g-24w4
CVE: CVE-2017-14242
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-jjgq-jq8g-24w4
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <6.0.1

## Details
SQL injection vulnerability in don/list.php in Dolibarr version 6.0.0 allows remote attackers to execute arbitrary SQL commands via the statut parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-14242
- https://github.com/Dolibarr/dolibarr/commit/33e2179b65331d9d9179b59d746817c5be1fecdb
- https://github.com/Dolibarr/dolibarr
