# [M] Pimcore Cross-site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-m4x3-xmjv-r778
CVE: CVE-2019-18982
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m4x3-xmjv-r778
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <6.3.0

## Details
`bundles/AdminBundle/Controller/Admin/EmailController.php` in Pimcore before 6.3.0 allows script execution in the Email Log preview window because of the lack of a Content-Security-Policy header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18982
- https://github.com/pimcore/pimcore/commit/e0b48faf7d29ce43a98825a0b230e88350ebcf78
- https://github.com/pimcore/pimcore
- https://github.com/pimcore/pimcore/compare/v6.2.3...v6.3.0
