# [M] Drupal Google Tag Cross-Site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-36vv-q5jv-94cj
CVE: CVE-2025-31682
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-04-01
Source: https://github.com/advisories/GHSA-36vv-q5jv-94cj
Type: github-advisory

## Affected
- Packagist: `drupal/google_tag` — affected >=0 <1.8.0
- Packagist: `drupal/google_tag` — affected >=2.0.0 <2.0.8

## Details
Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting') vulnerability in Drupal Google Tag allows Cross-Site Scripting (XSS). This issue affects Google Tag: from 0.0.0 before 1.8.0, from 2.0.0 before 2.0.8.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-31682
- https://git.drupalcode.org/project/google_tag
- https://www.drupal.org/sa-contrib-2025-011
