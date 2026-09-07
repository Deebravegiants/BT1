# [M] Dolibarr ERP and CRM contain XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qjq9-wx5j-jrg6
CVE: CVE-2017-17971
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qjq9-wx5j-jrg6
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <6.0.5

## Details
The test_sql_and_script_inject function in htdocs/main.inc.php in Dolibarr ERP/CRM 6.0.4 blocks some event attributes but neither onclick nor onscroll, which allows XSS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-17971
- https://github.com/Dolibarr/dolibarr/issues/8000
- https://github.com/Dolibarr/dolibarr/commit/b2feac9d90f2ecfd5916c4d49176ff1a138744c8
- https://github.com/Dolibarr/dolibarr
