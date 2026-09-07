# [M] Typo3 Security Misconfiguration in Frontend Session Handling

## Summary
Severity: Medium
Advisory: GHSA-qr5f-6fcv-w69q
Ecosystem: Packagist
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-qr5f-6fcv-w69q
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.27
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.8

## Details
It has been discovered session data of properly authenticated and logged in frontend users is kept and transformed into an anonymous user session during the logout process. This way the next user using the same client application gains access to previous session data.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2019-06-25-3.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2019-018
