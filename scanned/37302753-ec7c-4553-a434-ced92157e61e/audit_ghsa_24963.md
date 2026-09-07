# [H] Drupal Remote code execution

## Summary
Severity: High
Advisory: GHSA-rhx9-3qf7-r3j7
CVE: CVE-2017-6381
CWE: CWE-829
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-rhx9-3qf7-r3j7
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0 <8.2.7
- Packagist: `drupal/drupal` — affected >=8.0 <8.2.7

## Details
A 3rd party development library including with Drupal 8 development dependencies is vulnerable to remote code execution. This is mitigated by the default .htaccess protection against PHP execution, and the fact that Composer development dependencies aren't normal installed. You might be vulnerable to this if you are running a version of Drupal before 8.2.2. To be sure you aren't vulnerable, you can remove the <siteroot>/vendor/phpunit directory from your production deployments

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6381
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2017-6381.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2017-6381.yaml
- https://github.com/drupal/core
- https://www.drupal.org/SA-2017-001
- http://www.securityfocus.com/bid/96919
- http://www.securitytracker.com/id/1038058
