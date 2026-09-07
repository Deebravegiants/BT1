# [H] Cross-Site Scripting (XSS) vulnerabilities in Neos

## Summary
Severity: High
Advisory: GHSA-4542-p56h-8xww
Ecosystem: Packagist
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-4542-p56h-8xww
Type: github-advisory

## Affected
- Packagist: `typo3/neos` — affected >=1.2.0 <1.2.13
- Packagist: `typo3/neos` — affected >=2.0.0 <2.0.4

## Details
It has been discovered that Neos is vulnerable to several XSS attacks. Through these vulnerabilities, an attacker could tamper with page rendering, redirect victims to a fake login page, or capture user credentials (such as cookies). With the potential backdoor upload an attacker could gain access to the server itself, to an extent mainly limited by the server setup.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/neos/2015-11-23.yaml
- https://github.com/mneuhaus/TYPO3.Neos
- https://www.neos.io/blog/neos-sa-2015-002.html
