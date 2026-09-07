# [M] Typo3 Security Misconfiguration in User Session Handling

## Summary
Severity: Medium
Advisory: GHSA-g9rv-6g56-65h8
Ecosystem: Packagist
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-g9rv-6g56-65h8
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.25
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.6

## Details
When users change their password existing sessions for that particular user account are not revoked. A valid backend or frontend user account is required in order to make use of this vulnerability.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2019-05-07-2.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2019-011
