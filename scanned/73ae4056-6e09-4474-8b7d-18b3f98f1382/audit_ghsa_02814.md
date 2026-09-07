# [H] Drupal core Unrestricted Upload of File with Dangerous Type

## Summary
Severity: High
Advisory: GHSA-68jc-v27h-vhmw
CVE: CVE-2020-13671
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-68jc-v27h-vhmw
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=9.0.0 <9.0.8
- Packagist: `drupal/core` — affected >=8.9.0 <8.9.9
- Packagist: `drupal/core` — affected >=8.0.0 <8.8.11
- Packagist: `drupal/core` — affected >=7.0.0 <7.74
- Packagist: `drupal/drupal` — affected >=7.0.0 <7.74
- Packagist: `drupal/drupal` — affected >=8.0.0 <8.8.11
- Packagist: `drupal/drupal` — affected >=8.9.0 <8.9.9
- Packagist: `drupal/drupal` — affected >=9.0.0 <9.0.8

## Details
Drupal core does not properly sanitize certain filenames on uploaded files, which can lead to files being interpreted as the incorrect extension and served as the wrong MIME type or executed as PHP for certain hosting configurations. This issue affects: Drupal Drupal Core 9.0 versions prior to 9.0.8, 8.9 versions prior to 8.9.9, 8.8 versions prior to 8.8.11, and 7 versions prior to 7.74.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13671
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2020-13671.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2020-13671.yaml
- https://github.com/drupal/core
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5KSFM672XW3X6BR7TVKRD63SLZGKK437
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KWM4CTMEGAC4I2CHYNJVSROY4CVXVEUT
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5KSFM672XW3X6BR7TVKRD63SLZGKK437
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KWM4CTMEGAC4I2CHYNJVSROY4CVXVEUT
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2020-13671
- https://www.drupal.org/sa-core-2020-012
