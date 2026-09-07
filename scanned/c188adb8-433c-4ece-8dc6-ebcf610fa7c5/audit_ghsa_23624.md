# [M] Drupal access bypass vulnerability

## Summary
Severity: Medium
Advisory: GHSA-66mv-q8r2-hj8w
CVE: CVE-2017-6928
CWE: CWE-732
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-66mv-q8r2-hj8w
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=7.0 <7.57
- Packagist: `drupal/drupal` — affected >=7.0 <7.57

## Details
Drupal core 7.x versions before 7.57 when using Drupal's private file system, Drupal will check to make sure a user has access to a file before allowing the user to view or download it. This check fails under certain conditions in which one module is trying to grant access to the file and another is trying to deny it, leading to an access bypass vulnerability. This vulnerability is mitigated by the fact that it only occurs for unusual site configurations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6928
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2017-6928.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2017-6928.yaml
- https://github.com/drupal/core
- https://lists.debian.org/debian-lts-announce/2018/02/msg00030.html
- https://www.debian.org/security/2018/dsa-4123
- https://www.drupal.org/sa-core-2018-001
