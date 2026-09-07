# [M] Drupal Reflected file download vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qqxc-cppg-4xp8
CVE: CVE-2016-3168
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qqxc-cppg-4xp8
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=6.0 <6.38
- Packagist: `drupal/core` — affected >=7.0 <7.43
- Packagist: `drupal/drupal` — affected >=7.0 <7.43
- Packagist: `drupal/drupal` — affected >=6.0 <6.38

## Details
The System module in Drupal 6.x before 6.38 and 7.x before 7.43 might allow remote attackers to hijack the authentication of site administrators for requests that download and run files with arbitrary JSON-encoded content, aka a "reflected file download vulnerability."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3168
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2016-3168.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2016-3168.yaml
- https://github.com/drupal/core
- https://www.drupal.org/SA-CORE-2016-001
- http://www.debian.org/security/2016/dsa-3498
- http://www.openwall.com/lists/oss-security/2016/02/24/19
- http://www.openwall.com/lists/oss-security/2016/03/15/10
