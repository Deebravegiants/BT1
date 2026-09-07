# [H] Drupal Open redirect vulnerability in the drupal_goto function

## Summary
Severity: High
Advisory: GHSA-gxwx-c7m8-f95h
CVE: CVE-2016-3167
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-gxwx-c7m8-f95h
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=6.0 <6.38
- Packagist: `drupal/drupal` — affected >=6.0 <6.38

## Details
Open redirect vulnerability in the drupal_goto function in Drupal 6.x before 6.38, when used with PHP before 5.4.7, allows remote attackers to redirect users to arbitrary web sites and conduct phishing attacks via a double-encoded URL in the "destination" parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3167
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2016-3167.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2016-3167.yaml
- https://github.com/drupal/core
- https://www.drupal.org/SA-CORE-2016-001
- http://www.debian.org/security/2016/dsa-3498
- http://www.openwall.com/lists/oss-security/2016/02/24/19
- http://www.openwall.com/lists/oss-security/2016/03/15/10
