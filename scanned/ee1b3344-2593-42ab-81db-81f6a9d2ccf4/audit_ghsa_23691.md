# [H] Centreon SQL Injection

## Summary
Severity: High
Advisory: GHSA-5jxp-4x68-mhqc
CVE: CVE-2018-19312
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-5jxp-4x68-mhqc
Type: github-advisory

## Affected
- Packagist: `centreon/centreon` — affected >=18.0.0 <18.10.0
- Packagist: `centreon/centreon` — affected >=2.8.0 <2.8.24

## Details
Centreon 3.4.x (fixed in Centreon 18.10.0 and Centreon web 2.8.24) allows SQL Injection via the searchVM parameter to the main.php?p=20408 URI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19312
- https://github.com/centreon/centreon-archived/pull/6257
- https://github.com/centreon/centreon-archived/pull/6628
- https://documentation.centreon.com/docs/centreon/en/latest/release_notes/centreon-18.10/centreon-18.10.0.html
- https://documentation.centreon.com/docs/centreon/en/latest/release_notes/centreon-2.8/centreon-2.8.24.html
- http://www.roothc.com.br/1349-2
