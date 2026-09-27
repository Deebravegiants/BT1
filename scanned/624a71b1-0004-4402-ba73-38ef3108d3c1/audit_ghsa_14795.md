# [M] Zendframework URL Rewrite vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fh7r-58q4-6387
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-fh7r-58q4-6387
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework` — affected >=0 <2.5.0

## Details
zend-diactoros (and, by extension, Expressive), zend-http (and, by extension, Zend Framework MVC projects), and zend-feed (specifically, its PubSubHubbub sub-component) each contain a potential URL rewrite exploit. In each case, marshaling a request URI includes logic that introspects HTTP request headers that are specific to a given server-side URL rewrite mechanism.

When these headers are present on systems not running the specific URL rewriting mechanism, the logic would still trigger, allowing a malicious client or proxy to emulate the headers to request arbitrary content.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework/ZF2018-01.yaml
- https://github.com/zendframework/zendframework
- https://web.archive.org/web/20210618220447/https://framework.zend.com/security/advisory/ZF2018-01
