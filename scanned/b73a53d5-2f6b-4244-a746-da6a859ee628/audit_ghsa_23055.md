# [H] Drupal saving user accounts can sometimes grant the user all roles

## Summary
Severity: High
Advisory: GHSA-q3p9-8728-wq7x
CVE: CVE-2016-3169
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-q3p9-8728-wq7x
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=6.0 <6.38
- Packagist: `drupal/core` — affected >=7.0 <7.43
- Packagist: `drupal/drupal` — affected >=7.0 <7.43
- Packagist: `drupal/drupal` — affected >=6.0 <6.38

## Details
The User module in Drupal 6.x before 6.38 and 7.x before 7.43 allows remote attackers to gain privileges by leveraging contributed or custom code that calls the user_save function with an explicit category and loads all roles into the array.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3169
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2016-3169.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2016-3169.yaml
- https://github.com/drupal/core
- https://www.drupal.org/SA-CORE-2016-001
- http://www.debian.org/security/2016/dsa-3498
- http://www.openwall.com/lists/oss-security/2016/02/24/19
- http://www.openwall.com/lists/oss-security/2016/03/15/10
