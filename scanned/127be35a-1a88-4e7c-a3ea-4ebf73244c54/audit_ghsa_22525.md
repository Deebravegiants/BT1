# [H] Drupal Comment reply form allows access to restricted content

## Summary
Severity: High
Advisory: GHSA-2p28-5mvp-2j2r
CVE: CVE-2017-6926
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-2p28-5mvp-2j2r
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.4.0 <8.4.5
- Packagist: `drupal/core` — affected >=7.0 <7.57
- Packagist: `drupal/drupal` — affected >=8.4.0 <8.4.5
- Packagist: `drupal/drupal` — affected >=7.0 <7.57

## Details
In Drupal versions 8.4.x versions before 8.4.5 users with permission to post comments are able to view content and comments they do not have access to, and are also able to add comments to this content. This vulnerability is mitigated by the fact that the comment system must be enabled and the attacker must have permission to post comments.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6926
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2017-6926.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2017-6926.yaml
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2018-001
