# [M] Symfony Cross-site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g996-q5r8-w7g2
CVE: CVE-2019-10909
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-11-12
Source: https://github.com/advisories/GHSA-g996-q5r8-w7g2
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected >=2.7.0 <2.7.51
- Packagist: `symfony/symfony` — affected >=2.8.0 <2.8.50
- Packagist: `symfony/symfony` — affected >=3.0.0 <3.4.26
- Packagist: `symfony/symfony` — affected >=4.0.0 <4.1.12
- Packagist: `symfony/symfony` — affected >=4.2.0 <4.2.7
- Packagist: `symfony/framework-bundle` — affected >=2.7.0 <2.7.51
- Packagist: `symfony/framework-bundle` — affected >=2.8.0 <2.8.50
- Packagist: `symfony/framework-bundle` — affected >=3.0.0 <3.4.26
- Packagist: `symfony/framework-bundle` — affected >=4.0.0 <4.1.12
- Packagist: `symfony/framework-bundle` — affected >=4.2.0 <4.2.7
- Packagist: `drupal/core` — affected >=8.0.0 <8.5.15
- Packagist: `drupal/core` — affected >=8.6.0 <8.6.15
- Packagist: `drupal/drupal` — affected >=8.0.0 <8.5.15
- Packagist: `drupal/drupal` — affected >=8.6.0 <8.6.15

## Details
In Symfony before 2.7.51, 2.8.x before 2.8.50, 3.x before 3.4.26, 4.x before 4.1.12, and 4.2.x before 4.2.7, validation messages are not escaped, which can lead to XSS when user input is included. This is related to symfony/framework-bundle.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10909
- https://github.com/symfony/symfony/commit/ab4d05358c3d0dd1a36fc8c306829f68e3dd84e2
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2019-10909.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2019-10909.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/framework-bundle/CVE-2019-10909.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2019-10909.yaml
- https://symfony.com/blog/cve-2019-10909-escape-validation-messages-in-the-php-templating-engine
- https://symfony.com/cve-2019-10909
- https://www.drupal.org/sa-core-2019-005
- https://www.synology.com/security/advisory/Synology_SA_19_19
