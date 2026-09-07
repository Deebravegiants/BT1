# [C] Dolibarr SQL injection vulnerability in product/card.php

## Summary
Severity: Critical
Advisory: GHSA-jjqq-m998-53jf
CVE: CVE-2018-13447
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-jjqq-m998-53jf
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=7.0.3 <7.0.4

## Details
SQL injection vulnerability in product/card.php in Dolibarr ERP/CRM version 7.0.3 allows remote attackers to execute arbitrary SQL commands via the statut parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-13447
- https://github.com/Dolibarr/dolibarr/commit/36402c22eef49d60edd73a2f312f8e28fe0bd1cb
- https://github.com/Dolibarr/dolibarr
