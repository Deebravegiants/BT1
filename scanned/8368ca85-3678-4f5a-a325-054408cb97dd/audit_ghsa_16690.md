# [H] Drupal core Arbitrary PHP code execution

## Summary
Severity: High
Advisory: GHSA-gxxj-g9v8-w28p
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-gxxj-g9v8-w28p
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=7.0.0 <7.75
- Packagist: `drupal/core` — affected >=8.0.0 <8.8.12
- Packagist: `drupal/core` — affected >=8.9.0 <8.9.10
- Packagist: `drupal/core` — affected >=9.0.0 <9.0.9

## Details
The Drupal project uses the PEAR Archive_Tar library. The PEAR Archive_Tar library has released a security update that impacts Drupal. For more information please see:
CVE-2020-28948
CVE-2020-28949

Multiple vulnerabilities are possible if Drupal is configured to allow .tar, .tar.gz, .bz2, or .tlz file uploads and processes them.

To mitigate this issue, prevent untrusted users from uploading .tar, .tar.gz, .bz2, or .tlz files.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/2020-11-25.yaml
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2020-013
