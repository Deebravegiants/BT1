# [H] Drupal Core Arbitrary PHP code execution vulnerability

## Summary
Severity: High
Advisory: GHSA-x72f-ggjw-v5xh
CVE: CVE-2020-13664
CWE: CWE-77
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x72f-ggjw-v5xh
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.8.0 <8.8.8
- Packagist: `drupal/core` — affected >=8.9.0 <8.9.1
- Packagist: `drupal/core` — affected >=9.0.0 <9.0.1
- Packagist: `drupal/drupal` — affected >=8.8.0 <8.8.8
- Packagist: `drupal/drupal` — affected >=8.9.0 <8.9.1
- Packagist: `drupal/drupal` — affected >=9.0.0 <9.0.1

## Details
Arbitrary PHP code execution vulnerability in Drupal Core under certain circumstances. An attacker could trick an administrator into visiting a malicious site that could result in creating a carefully named directory on the file system. With this directory in place, an attacker could attempt to brute force a remote code execution vulnerability. Windows servers are most likely to be affected. This issue affects: Drupal Drupal Core 8.8.x versions prior to 8.8.8; 8.9.x versions prior to 8.9.1; 9.0.1 versions prior to 9.0.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13664
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2020-13664.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2020-13664.yaml
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2020-005
