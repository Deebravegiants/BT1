# [M] XSS in various backend modules due to (un)escaping in JS notification module

## Summary
Severity: Medium
Advisory: GHSA-jfxf-4frr-9j3q
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-25
Source: https://github.com/advisories/GHSA-jfxf-4frr-9j3q
Type: github-advisory

## Affected
- Packagist: `neos/neos` — affected >=3.3 <5.3.10
- Packagist: `neos/neos` — affected >=7.0.0 <7.0.9
- Packagist: `neos/neos` — affected >=7.1.0 <7.1.7
- Packagist: `neos/neos` — affected >=7.2.0 <7.2.6
- Packagist: `neos/neos` — affected >=7.3.0 <7.3.4
- Packagist: `neos/neos` — affected >=8.0.0 <8.0.2

## Details
The notification module displaying flash messages unscapes HTML coming from the server, resulting in XSS vulnerabilities with various names and labels of entities (eg. workspace title or media title). This however means you must be a logged in user with respective rights in the first place to leverage the attack vector.

## References
- https://github.com/neos/neos-development-collection/security/advisories/GHSA-jfxf-4frr-9j3q
- https://discuss.neos.io/t/neos-bugfix-releases-5-3-10-7-0-9-7-1-7-7-2-6-7-3-4-8-0-2/5930?u=kdambekalns
- https://github.com/neos/neos
- https://www.neos.io/blog/xss-in-various-backend-modules.html
