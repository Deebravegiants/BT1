# [M] TYPO3 Cross-Site Scripting in Form Framework

## Summary
Severity: Medium
Advisory: GHSA-4h5c-5g25-v7fh
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-4h5c-5g25-v7fh
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.23
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.4

## Details
Failing to properly encode user input, frontend forms handled by the form framework (system extension “form”) are vulnerable to cross-site scripting.

## References
- https://github.com/TYPO3/typo3/commit/79528f75e23c2832db321f36d777c1427553f764
- https://github.com/TYPO3/typo3/commit/a0c4348188559596f292ea03983171bde29d9870
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2019-01-22-6.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2019-007
