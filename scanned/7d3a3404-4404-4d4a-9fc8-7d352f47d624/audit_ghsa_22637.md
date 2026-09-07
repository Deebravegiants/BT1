# [C] Dolibarr SQL injection via the integer parameters qty and value_unit

## Summary
Severity: Critical
Advisory: GHSA-h34q-878w-w96r
CVE: CVE-2018-16809
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-h34q-878w-w96r
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=3.8

## Details
An issue was discovered in Dolibarr through 7.0.0. expensereport/card.php in the expense reports module allows SQL injection via the integer parameters qty and value_unit.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16809
- https://github.com/Dolibarr/dolibarr/issues/9449
- https://github.com/Dolibarr/dolibarr
