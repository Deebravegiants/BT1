# [M] Inadequate XSS Prevention in CodeIgniter/Framework Security Library

## Summary
Severity: Medium
Advisory: GHSA-q9j3-4ghj-6h57
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-q9j3-4ghj-6h57
Type: github-advisory

## Affected
- Packagist: `codeigniter/framework` — affected >=0 <3.0.3

## Details
The xss_clean() method in the Security Library of CodeIgniter/Framework, specifically in versions before 3.0.3, exhibited a vulnerability that allowed certain Cross-Site Scripting (XSS) vectors to bypass its intended protection mechanisms.

The xss_clean() method is designed to sanitize input data by removing potentially malicious content, thus preventing XSS attacks. However, in versions prior to 3.0.3, it was discovered that the method did not adequately mitigate specific XSS vectors, leaving a potential security gap.

## References
- https://github.com/bcit-ci/CodeIgniter/commit/71b1b3f5b2dcc0f4b652e9494e9853b82541ac8c
- https://github.com/FriendsOfPHP/security-advisories/blob/master/codeigniter/framework/2015-10-31-1.yaml
- https://github.com/bcit-ci/CodeIgniter
- https://www.codeigniter.com/user_guide/changelog.html#version-3-0-3
