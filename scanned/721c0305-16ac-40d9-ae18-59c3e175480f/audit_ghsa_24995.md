# [H] Drupal Form API ignores access restrictions on submit buttons

## Summary
Severity: High
Advisory: GHSA-4gh5-3hqj-x3pj
CVE: CVE-2016-3165
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4gh5-3hqj-x3pj
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=6.0 <6.38
- Packagist: `drupal/drupal` — affected >=6.0 <6.38

## Details
The Form API in Drupal 6.x before 6.38 ignores access restrictions on submit buttons, which might allow remote attackers to bypass intended access restrictions by leveraging permission to submit a form with a button that has "#access" set to FALSE in the server-side form definition.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3165
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2016-3165.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2016-3165.yaml
- https://github.com/drupal/core
- https://www.drupal.org/SA-CORE-2016-001
- http://www.debian.org/security/2016/dsa-3498
- http://www.openwall.com/lists/oss-security/2016/02/24/19
- http://www.openwall.com/lists/oss-security/2016/03/15/10
