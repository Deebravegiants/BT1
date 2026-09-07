# [H] OS Command Injection in Centreon

## Summary
Severity: High
Advisory: GHSA-2q95-593f-g7h7
CVE: CVE-2020-22345
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-2q95-593f-g7h7
Type: github-advisory

## Affected
- Packagist: `centreon/centreon` — affected >=0 <20.04.0

## Details
/graphStatus/displayServiceStatus.php in Centreon 19.10.8 allows remote attackers to execute arbitrary OS commands via shell metacharacters in the RRDdatabase_path parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-22345
- https://github.com/centreon/centreon/pull/8467#event-3163627607
- https://engindemirbilek.github.io/centreon-19.10-rce
- https://github.com/centreon/centreon
