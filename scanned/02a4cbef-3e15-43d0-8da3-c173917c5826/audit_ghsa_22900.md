# [M] Drupal external link injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wm86-w3cf-h6vm
CVE: CVE-2017-6932
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-wm86-w3cf-h6vm
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=7.0 <7.57
- Packagist: `drupal/drupal` — affected >=7.0 <7.57

## Details
Drupal core 7.x versions before 7.57 has an external link injection vulnerability when the language switcher block is used. A similar vulnerability exists in various custom and contributed modules. This vulnerability could allow an attacker to trick users into unwillingly navigating to an external site.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6932
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2017-6932.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2017-6932.yaml
- https://github.com/drupal/core
- https://lists.debian.org/debian-lts-announce/2018/02/msg00030.html
- https://www.debian.org/security/2018/dsa-4123
- https://www.drupal.org/sa-core-2018-001
