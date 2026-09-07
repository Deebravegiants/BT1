# [H] Drupal Cross-Site Request Forgery (CSRF)

## Summary
Severity: High
Advisory: GHSA-gxxq-fhc7-3jv9
CVE: CVE-2017-6379
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-gxxq-fhc7-3jv9
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.2.0 <8.2.7
- Packagist: `drupal/drupal` — affected >=8.2.0 <8.2.7

## Details
Some administrative paths in Drupal 8.2.x before 8.2.7 did not include protection for CSRF. This would allow an attacker to disable some blocks on a site. This issue is mitigated by the fact that users would have to know the block ID.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6379
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2017-6379.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2017-6379.yaml
- https://github.com/drupal/core
- https://www.drupal.org/SA-2017-001
- http://www.securityfocus.com/bid/96919
- http://www.securitytracker.com/id/1038058
