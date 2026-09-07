# [H] Drupal Incorrect cache context on password reset page

## Summary
Severity: High
Advisory: GHSA-98w5-wqp9-w466
CVE: CVE-2016-9450
CWE: CWE-345
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-98w5-wqp9-w466
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0 <8.2.3
- Packagist: `drupal/drupal` — affected >=8.0 <8.2.3

## Details
The user password reset form in Drupal 8.x before 8.2.3 allows remote attackers to conduct cache poisoning attacks by leveraging failure to specify a correct cache context.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9450
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2016-9450.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2016-9450.yaml
- https://github.com/drupal/core
- https://www.drupal.org/SA-CORE-2016-005
- http://www.securityfocus.com/bid/94367
