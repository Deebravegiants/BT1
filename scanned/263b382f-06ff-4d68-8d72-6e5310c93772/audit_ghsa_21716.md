# [H] Exposure of Resource to Wrong Sphere in Drupal Core

## Summary
Severity: High
Advisory: GHSA-mmjr-5q74-p3m4
CVE: CVE-2020-13670
CWE: CWE-668
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-12
Source: https://github.com/advisories/GHSA-mmjr-5q74-p3m4
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0.0 <8.8.10
- Packagist: `drupal/core` — affected >=8.9.0 <8.9.6
- Packagist: `drupal/core` — affected >=9.0.0 <9.0.6
- Packagist: `drupal/drupal` — affected >=8.0.0 <8.8.10
- Packagist: `drupal/drupal` — affected >=8.9.0 <8.9.6
- Packagist: `drupal/drupal` — affected >=9.0.0 <9.0.6

## Details
Information Disclosure vulnerability in file module of Drupal Core allows an attacker to gain access to the file metadata of a permanent private file that they do not have access to by guessing the ID of the file. This issue affects: Drupal Core 8.8.x versions prior to 8.8.10; 8.9.x versions prior to 8.9.6; 9.0.x versions prior to 9.0.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13670
- https://github.com/drupal/core/commit/f93a37b713b59f8d24e826bc74378099853eef3d
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2020-13670.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2020-13670.yaml
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2020-011
