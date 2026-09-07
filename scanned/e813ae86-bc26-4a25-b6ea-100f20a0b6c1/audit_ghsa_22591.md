# [M] Drupal Cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vhg8-x858-7wq6
CVE: CVE-2016-7571
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-vhg8-x858-7wq6
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0 <8.1.10
- Packagist: `drupal/drupal` — affected >=8.0 <8.1.10

## Details
Cross-site scripting (XSS) vulnerability in Drupal 8.x before 8.1.10 allows remote attackers to inject arbitrary web script or HTML via vectors involving an HTTP exception.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-7571
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2016-7571.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2016-7571.yaml
- https://github.com/drupal/core
- https://www.drupal.org/SA-CORE-2016-004
- http://www.securityfocus.com/bid/93101
- http://www.securitytracker.com/id/1036886
