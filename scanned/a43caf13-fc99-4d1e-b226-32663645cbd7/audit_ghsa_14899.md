# [M] Typo3 Arbitrary File Disclosure in Form Component

## Summary
Severity: Medium
Advisory: GHSA-wrpf-2x8h-82gr
CWE: CWE-200
Ecosystem: Packagist
Published: 2024-06-04
Source: https://github.com/advisories/GHSA-wrpf-2x8h-82gr
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.20

## Details
Failing to properly validate user input, the form component is susceptible to Arbitrary File Disclosure. A valid backend user account is needed to exploit this vulnerability. Only forms are vulnerable, which contain upload fields.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2016-04-12-2.yaml
- https://typo3.org/security/advisory/typo3-core-sa-2016-010
