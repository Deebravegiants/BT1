# [M] Pimcore XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-65p8-5423-fw3x
CVE: CVE-2019-18656
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-65p8-5423-fw3x
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <6.3.0

## Details
Pimcore 6prior to 6.3.0 has XSS in the translations grid because `bundles/AdminBundle/Resources/public/js/pimcore/settings/translations.js` mishandles certain HTML elements.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18656
- https://github.com/pimcore/pimcore/commit/ca036e9f86bb5cdb3dac0930ec131e5f35e26c5f
- https://github.com/pimcore/pimcore
