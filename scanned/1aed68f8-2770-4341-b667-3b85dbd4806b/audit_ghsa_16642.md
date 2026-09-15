# [M] friendsofsymfony/oauth2-php open redirection in oauth

## Summary
Severity: Medium
Advisory: GHSA-xm3x-4ph3-3x9c
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-xm3x-4ph3-3x9c
Type: github-advisory

## Affected
- Packagist: `friendsofsymfony/oauth2-php` — affected >=0 <1.3.0

## Details
An open redirection vulnerability has been identified in the friendsofsymfony/oauth2-php library, which could potentially expose users to unauthorized redirects during the OAuth authentication process. This vulnerability has been addressed by implementing an exact check for the domain and port, ensuring more secure redirection.

## References
- https://github.com/FriendsOfSymfony/oauth2-php/commit/606b8ea1c3c927c272ac1409116332ad5a2ed94c
- https://github.com/FriendsOfPHP/security-advisories/blob/master/friendsofsymfony/oauth2-php/2020-03-03-1.yaml
- https://github.com/FriendsOfSymfony/oauth2-php
- https://github.com/FriendsOfSymfony/oauth2-php/releases/tag/1.3.0
