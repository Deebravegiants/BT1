# [M] Typo3 Information Disclosure in Backend User Interface

## Summary
Severity: Medium
Advisory: GHSA-q9c4-9v5m-597p
Ecosystem: Packagist
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-q9c4-9v5m-597p
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.27
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.8

## Details
The element information component used to display properties of a certain record is susceptible to information disclosure. The list of references from or to the record is not properly checked for the backend user’s permissions. A valid backend user account is needed in order to exploit this vulnerability.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2019-06-25-1.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2019-014
