# [H] Drupal Open Redirect

## Summary
Severity: High
Advisory: GHSA-836p-6p4j-35cg
CVE: CVE-2016-3164
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-836p-6p4j-35cg
Type: github-advisory

## Affected
- Packagist: `drupal/drupal` — affected >=6.0 <6.38
- Packagist: `drupal/drupal` — affected >=7.0 <7.43
- Packagist: `drupal/drupal` — affected >=8.0 <8.0.4
- Packagist: `drupal/core` — affected >=8.0 <8.0.4
- Packagist: `drupal/core` — affected >=7.0 <7.43
- Packagist: `drupal/core` — affected >=6.0 <6.38

## Details
Drupal 6.x before 6.38, 7.x before 7.43, and 8.x before 8.0.4 might allow remote attackers to conduct open redirect attacks by leveraging (1) custom code or (2) a form shown on a 404 error page, related to path manipulation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3164
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2016-3164.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2016-3164.yaml
- https://github.com/drupal/drupal
- https://www.drupal.org/SA-CORE-2016-001
- http://www.debian.org/security/2016/dsa-3498
- http://www.openwall.com/lists/oss-security/2016/02/24/19
- http://www.openwall.com/lists/oss-security/2016/03/15/10
