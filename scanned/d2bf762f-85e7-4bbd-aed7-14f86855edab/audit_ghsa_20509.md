# [C] Arbitrary PHP code execution in Drupal

## Summary
Severity: Critical
Advisory: GHSA-8cw5-rv98-5c46
CVE: CVE-2019-6339
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-8cw5-rv98-5c46
Type: github-advisory

## Affected
- Packagist: `drupal/drupal` — affected >=7.0.0 <7.62.0
- Packagist: `drupal/drupal` — affected >=8.0.0 <8.5.9
- Packagist: `drupal/drupal` — affected >=8.6.0 <8.6.6
- Packagist: `drupal/core` — affected >=7.0.0 <7.62.0
- Packagist: `drupal/core` — affected >=8.0.0 <8.5.9
- Packagist: `drupal/core` — affected >=8.6.0 <8.6.6

## Details
In Drupal Core versions 7.x prior to 7.62, 8.6.x prior to 8.6.6, and 8.5.x prior to 8.5.9; A remote code execution vulnerability exists in
PHP's built-in phar stream wrapper when performing file operations on an untrusted phar:// URI. Some Drupal code (core, contrib, and custom) may be performing file operations on insufficiently validated user input, thereby being exposed to this vulnerability. This vulnerability is mitigated by the fact that such code paths typically require access to an administrative permission or an atypical configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-6339
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2019-6339.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2019-6339.yaml
- https://lists.debian.org/debian-lts-announce/2019/02/msg00004.html
- https://www.debian.org/security/2019/dsa-4370
- https://www.drupal.org/sa-core-2019-002
