# [H] Centreon SQL Injection

## Summary
Severity: High
Advisory: GHSA-79hg-357g-rrgv
CVE: CVE-2018-19271
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-79hg-357g-rrgv
Type: github-advisory

## Affected
- Packagist: `centreon/centreon` — affected >=18.0.0 <18.10.0
- Packagist: `centreon/centreon` — affected >=0 <2.8.28

## Details
Centreon 3.4.x (fixed in Centreon 18.10.0 and Centreon web 2.8.28) allows SQL Injection via the main.php searchH parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19271
- https://github.com/centreon/centreon-archived/pull/6625
- https://documentation.centreon.com/docs/centreon/en/latest/release_notes/centreon-18.10/centreon-18.10.0.html
- https://documentation.centreon.com/docs/centreon/en/latest/release_notes/centreon-2.8/centreon-2.8.28.html
- http://www.rootlabs.com.br/authenticated-sql-injection-in-centreon-3-4-x
