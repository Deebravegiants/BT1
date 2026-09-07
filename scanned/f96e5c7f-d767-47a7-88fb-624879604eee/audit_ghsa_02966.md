# [H] Unrestricted access to predictable file paths in hov/jobfair

## Summary
Severity: High
Advisory: GHSA-43g8-79x3-j898
CVE: CVE-2021-43564
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-11-15
Source: https://github.com/advisories/GHSA-43g8-79x3-j898
Type: github-advisory

## Affected
- Packagist: `hov/jobfair` — affected >=0 <1.0.13
- Packagist: `hov/jobfair` — affected >=2.0.0 <2.0.2

## Details
An issue was discovered in the jobfair (aka Job Fair) extension before 1.0.13 and 2.x before 2.0.2 for TYPO3. The extension fails to protect or obfuscate filenames of uploaded files. This allows unauthenticated users to download files with sensitive data by simply guessing the filename of uploaded files (e.g., uploads/tx_jobfair/cv.pdf).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43564
- https://github.com/nhovratov/jobfair
- https://typo3.org/security/advisory/typo3-ext-sa-2021-018
