# [M] Drupal core vulnerable to improper error handling

## Summary
Severity: Medium
Advisory: GHSA-52jr-x6h6-xj6g
CVE: CVE-2024-11942
CWE: CWE-390
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-12-05
Source: https://github.com/advisories/GHSA-52jr-x6h6-xj6g
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=10.0.0 <10.2.10

## Details
Under certain uncommon site configurations, a bug in the CKEditor 5 module can cause some image uploads to move the entire webroot to a different location on the file system. This could be exploited by a malicious user to take down a site.

The issue is mitigated by the fact that several non-default site configurations must exist simultaneously for this to occur.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-11942
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2024-002
