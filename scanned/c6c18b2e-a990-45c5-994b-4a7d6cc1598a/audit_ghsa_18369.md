# [M] TYPO3 CMS exposes sensitive information in an error message

## Summary
Severity: Medium
Advisory: GHSA-cvm2-5f78-g9m8
CVE: CVE-2025-59016
CWE: CWE-209
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-cvm2-5f78-g9m8
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=9.0.0 <12.4.37
- Packagist: `typo3/cms-core` — affected >=10.0.0 <12.4.37
- Packagist: `typo3/cms-core` — affected >=11.0.0 <12.4.37
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.4.37
- Packagist: `typo3/cms-core` — affected >=13.0.0 <13.4.18

## Details
Error messages containing sensitive information in the File Abstraction Layer in TYPO3 CMS versions 9.0.0-9.5.54, 10.0.0-10.4.53, 11.0.0-11.5.47, 12.0.0-12.4.36, and 13.0.0-13.4.17 allow backend users to disclose full file paths via failed low-level file-system operations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-59016
- https://github.com/TYPO3-CMS/core/commit/e1e4380a2d8e72228c597403f0463c21d6e1b8d9
- https://github.com/TYPO3-CMS/core
- https://typo3.org/security/advisory/typo3-core-sa-2025-020
