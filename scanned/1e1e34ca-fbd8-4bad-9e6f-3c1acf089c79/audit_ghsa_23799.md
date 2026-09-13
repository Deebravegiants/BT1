# [C] Centreon Privilege Escalation 

## Summary
Severity: Critical
Advisory: GHSA-f24j-f97w-65h8
CVE: CVE-2018-21025
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-f24j-f97w-65h8
Type: github-advisory

## Affected
- Packagist: `centreon/centreon` — affected >=0

## Details
In Centreon VM through 19.04.3, centreon-backup.pl allows attackers to become root via a crafted script, due to incorrect rights of sourced configuration files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-21025
- https://github.com/centreon/centreon-archived/issues/7082
- https://github.com/centreon/centreon-archived
- https://www.openwall.com/lists/oss-security/2019/10/08/1
