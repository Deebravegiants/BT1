# [C] Drupal SQL Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-hcq9-hmgf-6qr9
CVE: CVE-2011-2715
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-hcq9-hmgf-6qr9
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected 6.20

## Details
An SQL Injection vulnerability exists in Drupal 6.20 with Data 6.x-1.0-alpha14 due to insufficient sanitization of table names or column names.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-2715
- https://github.com/drupal/core
- https://www.drupal.org/node/1056470
- https://www.openwall.com/lists/oss-security/2011/07/26/8
