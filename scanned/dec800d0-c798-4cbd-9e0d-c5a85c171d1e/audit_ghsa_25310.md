# [C] Dolibarr Cross-site Scripting via the qty parameter in product/fournisseurs.php

## Summary
Severity: Critical
Advisory: GHSA-pm57-926c-28mr
CVE: CVE-2019-19212
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pm57-926c-28mr
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=3.0

## Details
Dolibarr ERP/CRM 3.0 through 10.0.3 allows XSS via the qty parameter to product/fournisseurs.php (product price screen).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19212
- https://github.com/Dolibarr/dolibarr
- https://herolab.usd.de/en/security-advisories
- https://herolab.usd.de/security-advisories/usd-2019-0054
- https://www.dolibarr.org/forum/dolibarr-changelogs
