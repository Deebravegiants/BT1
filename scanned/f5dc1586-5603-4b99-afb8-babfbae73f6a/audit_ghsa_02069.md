# [H] Command Injection in Centreon

## Summary
Severity: High
Advisory: GHSA-jmgg-wx67-7qfv
CVE: CVE-2020-13252
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-22
Source: https://github.com/advisories/GHSA-jmgg-wx67-7qfv
Type: github-advisory

## Affected
- Packagist: `centreon/centreon` — affected >=0 <19.04.15

## Details
Centreon before 19.04.15 allows remote attackers to execute arbitrary OS commands by placing shell metacharacters in RRDdatabase_status_path (via a main.get.php request) and then visiting the include/views/graphs/graphStatus/displayServiceStatus.php page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13252
- https://github.com/centreon/centreon/pull/8467
- https://engindemirbilek.github.io/centreon-19.10-rce
- https://github.com/EnginDemirbilek/EnginDemirbilek.github.io/blob/master/centreon-19.10-rce.html
- https://github.com/centreon/centreon/compare/19.04.13...19.04.15
