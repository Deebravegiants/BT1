# [M] TYPO3 CMS has an open‑redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-72jf-5fg5-3cw3
CVE: CVE-2025-59013
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-72jf-5fg5-3cw3
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=9.0.0 <12.4.37
- Packagist: `typo3/cms-core` — affected >=10.0.0 <12.4.37
- Packagist: `typo3/cms-core` — affected >=11.0.0 <12.4.37
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.4.37
- Packagist: `typo3/cms-core` — affected >=13.0.0 <13.4.18

## Details
An open‑redirect vulnerability in GeneralUtility::sanitizeLocalUrl of TYPO3 CMS 9.0.0–9.5.54, 10.0.0–10.4.53, 11.0.0–11.5.47, 12.0.0–12.4.36, and 13.0.0–13.4.17 allows an attacker to redirect users to arbitrary external sites, enabling phishing attacks by supplying a manipulated, sanitized URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-59013
- https://github.com/TYPO3-CMS/core/commit/862b9da870815132c31119cd85bc454a5010793c
- https://github.com/TYPO3-CMS/core
- https://typo3.org/security/advisory/typo3-core-sa-2025-017
