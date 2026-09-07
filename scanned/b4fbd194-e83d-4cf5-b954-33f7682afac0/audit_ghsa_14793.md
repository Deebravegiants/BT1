# [M] Cross-Site Scripting in TYPO3 Backend

## Summary
Severity: Medium
Advisory: GHSA-86r8-4g3w-7xjp
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-86r8-4g3w-7xjp
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.26
- Packagist: `typo3/cms` — affected >=7.6.0 <7.6.10
- Packagist: `typo3/cms` — affected >=8.0.0 <8.2.1

## Details
Failing to properly encode user input, some backend components are vulnerable to Cross-Site Scripting. A valid backend user account is needed to exploit this vulnerability.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2016-07-19-1.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2016-014
