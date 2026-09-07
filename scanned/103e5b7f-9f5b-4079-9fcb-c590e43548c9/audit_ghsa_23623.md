# [M] Centreon Sensitive Data Exposure

## Summary
Severity: Medium
Advisory: GHSA-rx4j-x3fh-9qwg
CVE: CVE-2019-17106
CWE: CWE-312
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rx4j-x3fh-9qwg
Type: github-advisory

## Affected
- Packagist: `centreon/centreon` — affected >=0 <2.8.30

## Details
In Centreon Web through 2.8.29, disclosure of external components' passwords allows authenticated attackers to move laterally to external components.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17106
- https://github.com/centreon/centreon-archived/issues/7098
- https://github.com/centreon/centreon-archived/pull/9311
- https://github.com/centreon/centreon-archived
- https://www.openwall.com/lists/oss-security/2019/10/08/1
