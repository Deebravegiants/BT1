# [M] sensiolabs/connect has a Cross-Site Request Forgery Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6wqp-7g94-f69j
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-21
Source: https://github.com/advisories/GHSA-6wqp-7g94-f69j
Type: github-advisory

## Affected
- Packagist: `sensiolabs/connect` — affected >=0 <4.2.3

## Details
Versions of sensiolabs/connect prior to 4.2.3 are affected by a Cross-Site Request Forgery (CSRF) vulnerability due to the absence of the state parameter in OAuth requests. The lack of proper state parameter handling exposes applications to CSRF attacks during the OAuth authentication flow.

## References
- https://github.com/sensiolabs/connect/pull/63
- https://github.com/symfonycorp/connect/commit/9522aa774e8a0f8a61e709d828e6cc34c4c1e703
- https://github.com/FriendsOfPHP/security-advisories/blob/master/sensiolabs/connect/2018-06-08-1.yaml
- https://github.com/symfonycorp/connect
