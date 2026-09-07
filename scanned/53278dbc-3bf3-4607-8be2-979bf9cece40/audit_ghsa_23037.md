# [M] Drupal sensitive information disclosure

## Summary
Severity: Medium
Advisory: GHSA-p745-347h-hjfw
CVE: CVE-2016-9449
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-p745-347h-hjfw
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=7.0 <7.52
- Packagist: `drupal/core` — affected >=8.0 <8.2.3
- Packagist: `drupal/drupal` — affected >=8.0 <8.2.3
- Packagist: `drupal/drupal` — affected >=7.0 <7.52

## Details
The taxonomy module in Drupal 7.x before 7.52 and 8.x before 8.2.3 might allow remote authenticated users to obtain sensitive information about taxonomy terms by leveraging inconsistent naming of access query tags.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9449
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2016-9449.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2016-9449.yaml
- https://github.com/drupal/core
- https://www.drupal.org/SA-CORE-2016-005
- http://www.debian.org/security/2016/dsa-3718
- http://www.securityfocus.com/bid/94367
