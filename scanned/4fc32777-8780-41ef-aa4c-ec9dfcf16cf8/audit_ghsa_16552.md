# [M] Drupal Anonymous Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-x6v2-xmrq-574j
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-x6v2-xmrq-574j
Type: github-advisory

## Affected
- Packagist: `drupal/drupal` — affected >=8.0.0 <8.5.8
- Packagist: `drupal/drupal` — affected >=8.6.0 <8.6.2

## Details
Drupal core and contributed modules frequently use a "destination" query string parameter in URLs to redirect users to a new destination after completing an action on the current page. Under certain circumstances, malicious users can use this parameter to construct a URL that will trick users into being redirected to a 3rd party website, thereby exposing the users to potential social engineering attacks.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/2018-10-17-3.yaml
- https://github.com/drupal/drupal
- https://www.drupal.org/sa-core-2018-006
