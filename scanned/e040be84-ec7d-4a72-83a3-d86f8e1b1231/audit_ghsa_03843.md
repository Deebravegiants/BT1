# [M] Missing Authorization in Drupal

## Summary
Severity: Medium
Advisory: GHSA-v3f6-f29f-rgvp
CVE: CVE-2017-6923
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-10-10
Source: https://github.com/advisories/GHSA-v3f6-f29f-rgvp
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0 <8.3.7
- Packagist: `drupal/drupal` — affected >=8.0 <8.3.7

## Details
In Drupal 8.x prior to 8.3.7 When creating a view, you can optionally use Ajax to update the displayed data via filter parameters. The views subsystem/module did not restrict access to the Ajax endpoint to only views configured to use Ajax. This is mitigated if you have access restrictions on the view. It is best practice to always include some form of access restrictions on all views, even if you are using another module to display them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6923
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2017-6923.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2017-6923.yaml
- https://www.drupal.org/SA-CORE-2017-004
- https://www.drupal.org/forum/newsletters/security-advisories-for-drupal-core/2017-08-16/drupal-core-multiple
- http://www.securityfocus.com/bid/100368
- http://www.securitytracker.com/id/1039200
