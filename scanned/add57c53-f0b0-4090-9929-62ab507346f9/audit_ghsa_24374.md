# [H] TYPO3 Image Processing susceptible to Code Execution

## Summary
Severity: High
Advisory: GHSA-3w4h-r27h-4r2w
CVE: CVE-2019-11832
CWE: CWE-20, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3w4h-r27h-4r2w
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=8.0.0 <8.7.25
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.6
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.25
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.6

## Details
TYPO3 8.x before 8.7.25 and 9.x before 9.5.6 is susceptible to remote code execution because it does not properly configure the applications used for image processing, as demonstrated by ImageMagick or GraphicsMagick.
For a successful exploit, the GhostScript binary `gs` must be available on the server system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11832
- https://github.com/github/advisory-database/pull/3530
- https://github.com/TYPO3/typo3/commit/2c04eeac44733fda491f92c697f88c1337d19c79
- https://github.com/TYPO3/typo3/commit/51fdb774a57ee30e8d60c0e33b4a0b92d775739e
- https://github.com/TYPO3/typo3/commit/e845d90b82b2f72ab12a9e37f15082297832beca
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2019-11832.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2019-11832.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2019-012
