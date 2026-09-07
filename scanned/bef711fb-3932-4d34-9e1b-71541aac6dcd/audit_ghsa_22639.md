# [M] Drupal CRLF injection vulnerability in the drupal_set_header function

## Summary
Severity: Medium
Advisory: GHSA-fg5q-r2q5-qmh3
CVE: CVE-2016-3166
CWE: CWE-113
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-fg5q-r2q5-qmh3
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=6.0 <6.38
- Packagist: `drupal/drupal` — affected >=6.0 <6.38

## Details
CRLF injection vulnerability in the drupal_set_header function in Drupal 6.x before 6.38, when used with PHP before 5.1.2, allows remote attackers to inject arbitrary HTTP headers and conduct HTTP response splitting attacks by leveraging a module that allows user-submitted data to appear in HTTP headers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3166
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2016-3166.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2016-3166.yaml
- https://github.com/drupal/core
- https://www.drupal.org/SA-CORE-2016-001
- http://www.debian.org/security/2016/dsa-3498
- http://www.openwall.com/lists/oss-security/2016/02/24/19
- http://www.openwall.com/lists/oss-security/2016/03/15/10
