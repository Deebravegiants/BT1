# [H] Drupal File upload access bypass and denial of service

## Summary
Severity: High
Advisory: GHSA-w2pj-c8x5-jvg2
CVE: CVE-2016-3162
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-w2pj-c8x5-jvg2
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=7.0 <7.43
- Packagist: `drupal/core` — affected >=8.0 <8.0.4
- Packagist: `drupal/drupal` — affected >=8.0 <8.0.4
- Packagist: `drupal/drupal` — affected >=7.0 <7.43

## Details
The File module in Drupal 7.x before 7.43 and 8.x before 8.0.4 allows remote authenticated users to bypass access restrictions and read, delete, or substitute a link to a file uploaded to an unprocessed form by leveraging permission to create content or comment and upload files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3162
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2016-3162.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2016-3162.yaml
- https://github.com/drupal/core
- https://www.drupal.org/SA-CORE-2016-001
- http://www.debian.org/security/2016/dsa-3498
- http://www.openwall.com/lists/oss-security/2016/02/24/19
- http://www.openwall.com/lists/oss-security/2016/03/15/10
