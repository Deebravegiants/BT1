# [M] Cross-site Scripting in the yoast_seo TYPO3 extension

## Summary
Severity: Medium
Advisory: GHSA-28w5-j8xj-2xwc
CVE: CVE-2021-36788
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-28w5-j8xj-2xwc
Type: github-advisory

## Affected
- Packagist: `yoast-seo-for-typo3/yoast_seo` — affected >=0 <7.2.3

## Details
The extension fails to properly encode user input for output in HTML context. A TYPO3 backend user account is required to exploit the vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36788
- https://github.com/Yoast/Yoast-SEO-for-TYPO3/commit/a8278dae97dce8cd0722d38f7f5a30b563668590
- https://github.com/Yoast/Yoast-SEO-for-TYPO3
- https://typo3.org/security/advisory/typo3-ext-sa-2021-012
