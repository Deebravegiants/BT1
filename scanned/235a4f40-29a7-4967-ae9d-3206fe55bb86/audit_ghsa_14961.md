# [H] TYPO3 Remote Code Execution in third party library swiftmailer

## Summary
Severity: High
Advisory: GHSA-g4pf-3jvq-2gcw
CWE: CWE-94
Ecosystem: Packagist
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-g4pf-3jvq-2gcw
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.30
- Packagist: `typo3/cms` — affected >=7.6.0 <7.6.15
- Packagist: `typo3/cms` — affected >=8.0.0 <8.5.1

## Details
TYPO3 uses the package swiftmailer/swiftmailer for mail actions. This package is known to be vulnerable to Remote Code Execution.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2017-01-03-1.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2017-001
