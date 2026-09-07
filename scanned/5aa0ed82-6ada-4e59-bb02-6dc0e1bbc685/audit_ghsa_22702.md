# [M] silverstripe-advancedreports vulnerable to XSS

## Summary
Severity: Medium
Advisory: GHSA-8f2x-hv9r-mh9r
CVE: CVE-2020-25102
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8f2x-hv9r-mh9r
Type: github-advisory

## Affected
- Packagist: `silverstripe-australia/advancedreports` — affected >=1.0

## Details
silverstripe-advancedreports (aka the Advanced Reports module for SilverStripe) 1.0 through 2.0 is vulnerable to Cross-Site Scripting (XSS) because it is possible to inject and store malicious JavaScript code. The affects `admin/advanced-reports/DataObjectReport/EditForm/field/DataObjectReport/item` (aka report preview) when an SVG document is provided in the Description parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25102
- https://gist.github.com/ahpaleus/c3bd2d41d306544ca3158569335d12f2
- https://github.com/nyeholt/silverstripe-advancedreports
- https://github.com/nyeholt/silverstripe-advancedreports/releases
