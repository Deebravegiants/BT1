# [M] GeniXCMS Cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-478j-mcrr-3877
CVE: CVE-2017-14740
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-478j-mcrr-3877
Type: github-advisory

## Affected
- Packagist: `genix/cms` — affected 1.1.0

## Details
Cross-site scripting (XSS) vulnerability in GeniXCMS 1.1.0 allows remote authenticated users to inject arbitrary web script or HTML via the Menu ID when adding a menu.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-14740
- https://github.com/GeniXCMS/GeniXCMS
- https://github.com/faizzaidi/GeniXCMS-Version-1.1.0-Cross-Site-Scripting-XSS
