# [H] Drupal Brute force amplification attacks via XML-RPC

## Summary
Severity: High
Advisory: GHSA-h3r9-pjmr-f938
CVE: CVE-2016-3163
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-h3r9-pjmr-f938
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=7.0 <7.43
- Packagist: `drupal/core` — affected >=6.0 <6.38
- Packagist: `drupal/drupal` — affected >=7.0 <7.43
- Packagist: `drupal/drupal` — affected >=6.0 <6.38

## Details
The XML-RPC system in Drupal 6.x before 6.38 and 7.x before 7.43 might make it easier for remote attackers to conduct brute-force attacks via a large number of calls made at once to the same method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3163
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2016-3163.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2016-3163.yaml
- https://github.com/drupal/core
- https://www.drupal.org/SA-CORE-2016-001
- http://www.debian.org/security/2016/dsa-3498
- http://www.openwall.com/lists/oss-security/2016/02/24/19
- http://www.openwall.com/lists/oss-security/2016/03/15/10
