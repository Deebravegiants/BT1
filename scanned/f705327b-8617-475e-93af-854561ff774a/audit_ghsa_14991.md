# [H] Flow Bugfix Releases for Entity Security

## Summary
Severity: High
Advisory: GHSA-vh6j-wv25-8qxr
Ecosystem: Packagist
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-vh6j-wv25-8qxr
Type: github-advisory

## Affected
- Packagist: `typo3/flow` — affected >=3.0.0 <3.0.12
- Packagist: `typo3/flow` — affected >=3.1.0 <3.1.10
- Packagist: `typo3/flow` — affected >=3.2.0 <3.2.13
- Packagist: `typo3/flow` — affected >=3.3.0 <3.3.13
- Packagist: `typo3/flow` — affected >=4.0.0 <4.0.6

## Details
If you had used entity security and wanted to secure entities not just based on the user's role, but on some property of the user (like the company he belongs to), entity security did not work properly together with the doctrine query cache. This could lead to other users re-using SQL queries from the cache which were built for other users; and thus users could see entities which were not destined for them.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/flow/2017-04-12.yaml
- https://github.com/neos/flow
- https://www.neos.io/blog/flow-bugfix-releases-for-entity-security.html
