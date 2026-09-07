# [M] TYPO3 Cross-Site Scripting in link validator component

## Summary
Severity: Medium
Advisory: GHSA-cg4m-qjjp-7497
Ecosystem: Packagist
Published: 2024-06-03
Source: https://github.com/advisories/GHSA-cg4m-qjjp-7497
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.18
- Packagist: `typo3/cms` — affected >=7.6.0 <7.6.3

## Details
Failing to sanitize content from editors, the link validator component is susceptible to Cross-Site Scripting. A valid editor account with access to content which is scanned by the link validator component is required to exploit this vulnerability.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2016-02-16-2.yaml
- https://typo3.org/security/advisory/typo3-core-sa-2016-002
- https://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2016-002
