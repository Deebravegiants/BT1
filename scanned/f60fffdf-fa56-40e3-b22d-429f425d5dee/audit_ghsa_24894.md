# [H] Drupal arbitrary code execution

## Summary
Severity: High
Advisory: GHSA-69g8-g9jq-74v7
CVE: CVE-2016-3171
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-69g8-g9jq-74v7
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=6.0 <6.38
- Packagist: `drupal/drupal` — affected >=6.0 <6.38

## Details
Drupal 6.x before 6.38, when used with PHP before 5.4.45, 5.5.x before 5.5.29, or 5.6.x before 5.6.13, might allow remote attackers to execute arbitrary code via vectors related to session data truncation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3171
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2016-3171.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2016-3171.yaml
- https://github.com/drupal/core
- https://www.drupal.org/SA-CORE-2016-001
- http://www.debian.org/security/2016/dsa-3498
- http://www.openwall.com/lists/oss-security/2016/02/24/19
- http://www.openwall.com/lists/oss-security/2016/03/15/10
