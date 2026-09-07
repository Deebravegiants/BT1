# [M] TYPO3 Cross-Site Scripting in Link Handling

## Summary
Severity: Medium
Advisory: GHSA-xgmx-j3hv-jh9x
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-xgmx-j3hv-jh9x
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=10.0.0 <10.2.1
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.30
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.12

## Details
It has been discovered that `t3://` URL handling and typolink functionality are vulnerable to cross-site scripting. Not only regular backend forms are affected but also frontend extensions which use the rendering with typolink.

## References
- https://github.com/TYPO3/typo3/commit/25f796b94e23bac77e836bd38f53ce998c094901
- https://github.com/TYPO3/typo3/commit/64db88b9b61bb67b3b44145dc8e0e1ef251da45e
- https://github.com/TYPO3/typo3/commit/a35c42e9bcb020e16016d1c146354513a9856bc0
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2019-12-17-2.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2019-022
