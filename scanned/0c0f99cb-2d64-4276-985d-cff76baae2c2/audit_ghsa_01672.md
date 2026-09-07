# [M] Cross-Site Scripting in SVG Sanitizer

## Summary
Severity: Medium
Advisory: GHSA-59cf-m7v5-wh5w
CVE: CVE-2020-11070
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-05-13
Source: https://github.com/advisories/GHSA-59cf-m7v5-wh5w
Type: github-advisory

## Affected
- Packagist: `t3g/svg-sanitizer` — affected >=0 <1.0.3

## Details
Slightly invalid or incomplete SVG markup is not correctly processed and thus not sanitized at all. Albeit the markup is not valid it still is evaluated in browsers and leads to cross-site scripting.

An updated version 1.0.3 is available from the TYPo3 extension manager and at https://extensions.typo3.org/extension/download/svg_sanitizer/1.0.3/zip/
Users of the extension are advised to update the extension as soon as possible.

## References
- https://github.com/TYPO3GmbH/svg_sanitizer/security/advisories/GHSA-59cf-m7v5-wh5w
- https://nvd.nist.gov/vuln/detail/CVE-2020-11070
