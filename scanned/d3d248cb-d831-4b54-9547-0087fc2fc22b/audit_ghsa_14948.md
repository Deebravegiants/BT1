# [M] Cross-Site Scripting in TYPO3 CMS Backend

## Summary
Severity: Medium
Advisory: GHSA-v4qr-8h2v-qpjx
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-v4qr-8h2v-qpjx
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.5

## Details
Failing to properly encode user input, backend forms are vulnerable to Cross-Site Scripting. A valid backend user account is needed to exploit this vulnerability.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2017-09-05-1.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2017-004
- https://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2017-004
