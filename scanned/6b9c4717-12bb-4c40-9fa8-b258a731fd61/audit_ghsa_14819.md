# [H] typo3 Information Disclosure Security Note

## Summary
Severity: High
Advisory: GHSA-g4xv-r3qw-v3q2
Ecosystem: Packagist
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-g4xv-r3qw-v3q2
Type: github-advisory

## Affected
- Packagist: `typo3/neos` — affected >=2.3.0 <2.3.99
- Packagist: `typo3/neos` — affected >=3.0.0 <3.0.20
- Packagist: `typo3/neos` — affected >=3.1.0 <3.1.18
- Packagist: `typo3/neos` — affected >=3.2.0 <3.2.14
- Packagist: `typo3/neos` — affected >=3.3.0 <3.3.23
- Packagist: `typo3/neos` — affected >=4.0.0 <4.0.17
- Packagist: `typo3/neos` — affected >=4.1.0 <4.1.16
- Packagist: `typo3/neos` — affected >=4.2.0 <4.2.12
- Packagist: `typo3/neos` — affected >=4.3.0 <4.3.3

## Details
Due to reports it has been validated that internal workspaces in Neos are accessible without authentication. Some users assumed this is a planned feature but it is not. A workspace preview should be an additional feature with respective security measures in place.

Note that this only allows reading of internal workspaces not writing. And for clarification, an internal workspace is a workspace that is non public and doesn't have an owner.

Given that an internal workspace exists in your installation, it is possible to view a page in context of that workspace by opening a link in this format:

https://domain/path/to/page.html@workspace-name

The issue is quite problematic when exploited but at the same time slightly less impactful than it sounds. First of all there is no default internal workspace, so the issue affects only workspaces created by users. That also means the workspace-name, which will also always include a hash is individual to a project and an exploiter must get hold of the workspace-name including the hash. This is non trivial as there is no indication of the existence of it, but obviously brute force and educated guessed can be made.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/neos/2019-06-17.yaml
- https://github.com/mneuhaus/TYPO3.Neos
- https://www.neos.io/blog/neos-workspace-disclosure-security.html
