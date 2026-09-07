# [M] Drupal Denial of service via transliterate mechanism

## Summary
Severity: Medium
Advisory: GHSA-jpj8-49hr-wcwv
CVE: CVE-2016-9452
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-jpj8-49hr-wcwv
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0 <8.2.3
- Packagist: `drupal/drupal` — affected >=8.0 <8.2.3

## Details
The transliterate mechanism in Drupal 8.x before 8.2.3 allows remote attackers to cause a denial of service via a crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9452
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2016-9452.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2016-9452.yaml
- https://github.com/drupal/core
- https://www.drupal.org/SA-CORE-2016-005
- http://www.securityfocus.com/bid/94367
