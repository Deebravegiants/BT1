# [M] Time-Based Information Disclosure Vulnerability in Flow

## Summary
Severity: Medium
Advisory: GHSA-r6mm-wmhf-849m
Ecosystem: Packagist
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-r6mm-wmhf-849m
Type: github-advisory

## Affected
- Packagist: `typo3/flow` — affected >=2.3.0 <2.3.16
- Packagist: `typo3/flow` — affected >=3.0.0 <3.0.10
- Packagist: `typo3/flow` — affected >=3.1.0 <3.1.7
- Packagist: `typo3/flow` — affected >=3.2.0 <3.2.7
- Packagist: `typo3/flow` — affected >=3.3.0 <3.3.5

## Details
The PersistedUsernamePasswordProvider was prone to a information disclosure of account existance based on timing attacks as the hashing of passwords was only done in case an account was found. We changed the core so that the provider always does a password comparison in case credentials were submitted at all.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/flow/2016-11-01.yaml
- https://github.com/neos/flow
- https://www.neos.io/blog/flow-sa-2016-001.html
