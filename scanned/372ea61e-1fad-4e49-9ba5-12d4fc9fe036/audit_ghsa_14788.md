# [M] TYPO3 Cross-Site Scripting in legacy form component

## Summary
Severity: Medium
Advisory: GHSA-vgm8-r9gm-fw59
Ecosystem: Packagist
Published: 2024-06-03
Source: https://github.com/advisories/GHSA-vgm8-r9gm-fw59
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.18

## Details
Failing to sanitize content from editors, the legacy form component is susceptible to Cross-Site Scripting. A valid editor account with access to a form content element is required to exploit this vulnerability.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2016-02-16-3.yaml
- https://typo3.org/security/advisory/typo3-core-sa-2016-003
- https://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2016-003
