# [H]  "Newsletter subscriber management" (fp_newsletter) TYPO3 extension leaks subscriber data

## Summary
Severity: High
Advisory: GHSA-r44w-pfx8-28jv
CVE: CVE-2022-47411
CWE: CWE-200, CWE-668
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-14
Source: https://github.com/advisories/GHSA-r44w-pfx8-28jv
Type: github-advisory

## Affected
- Packagist: `fixpunkt/fp-newsletter` — affected >=0 <1.1.1
- Packagist: `fixpunkt/fp-newsletter` — affected >=1.2.0 <2.1.2
- Packagist: `fixpunkt/fp-newsletter` — affected >=3.0.0 <3.2.6

## Details
An issue was discovered in the fp_newsletter (aka Newsletter subscriber management) extension before 1.1.1, 1.2.0, 2.x before 2.1.2, 2.2.1 through 2.4.0, and 3.x before 3.2.6 for TYPO3. Data about subscribers may be obtained via unsubscribeAction operations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-47411
- https://github.com/bihor/fp_newsletter
- https://typo3.org/security/advisory/typo3-ext-sa-2022-017
