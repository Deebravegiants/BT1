# [M] TYPO3 Cross-Site Scripting in Fluid ViewHelpers

## Summary
Severity: Medium
Advisory: GHSA-85ch-44w7-rf32
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-85ch-44w7-rf32
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.23
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.4

## Details
Failing to properly encode user input, templates using built-in Fluid ViewHelpers are vulnerable to cross-site scripting.

## References
- https://github.com/TYPO3/typo3/commit/732c4acfaeaa7fd193674cd4d1ca7e369e21b96f
- https://github.com/TYPO3/typo3/commit/c94f566514eaff62dd836541c99b438ac55f6842
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2019-01-22-4.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2019-005
