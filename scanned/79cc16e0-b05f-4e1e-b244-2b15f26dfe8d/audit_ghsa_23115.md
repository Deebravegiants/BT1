# [H] Drupal editor module incorrectly checks access to inline private files

## Summary
Severity: High
Advisory: GHSA-w7qx-vwr9-2j3r
CVE: CVE-2017-6377
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-w7qx-vwr9-2j3r
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.2.0 <8.2.7
- Packagist: `drupal/drupal` — affected >=8.2.0 <8.2.7

## Details
When adding a private file via the editor in Drupal 8.2.x before 8.2.7, the editor will not correctly check access for the file being attached, resulting in an access bypass.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6377
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2017-6377.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2017-6377.yaml
- https://github.com/drupal/drupal
- https://www.drupal.org/SA-2017-001
- http://www.securityfocus.com/bid/96919
- http://www.securitytracker.com/id/1038058
