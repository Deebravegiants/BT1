# [H] SQL Injection in Dolibarr

## Summary
Severity: High
Advisory: GHSA-vrgp-3ph6-2wwq
CVE: CVE-2021-36625
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-01
Source: https://github.com/advisories/GHSA-vrgp-3ph6-2wwq
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <14.0.0

## Details
An SQL Injection vulnerability exists in Dolibarr ERP/CRM 13.0.2 (fixed version is 14.0.0) via a POST request to the country_id parameter in an UPDATE statement.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36625
- https://github.com/Dolibarr/dolibarr/commit/abb1ad6bf0469eccd2b58beb20bdabc18fc36e22
- https://github.com/Dolibarr/dolibarr
