# [C] hull.js Code Injection Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-q849-wxrc-vqrp
CWE: CWE-94
Ecosystem: npm
Published: 2024-12-02
Source: https://github.com/advisories/GHSA-q849-wxrc-vqrp
Type: github-advisory

## Affected
- npm: `hull.js` — affected >=0.2.2 <1.0.10

## Details
Versions of the library from 0.2.2 to 1.0.9 are vulnerable to the arbitrary code execution due to unsafe usage of `new Function(...)` in the module that handles points format. Applications passing the 3rd parameter to the `hull` function without sanitising may be impacted. The vulnerability has been fixed in version 1.0.10, please update the library. Check project homepage on GitHub to see how to fetch the latest version: https://github.com/andriiheonia/hull?tab=readme-ov-file#npm-package

## References
- https://github.com/AndriiHeonia/hull/security/advisories/GHSA-q849-wxrc-vqrp
- https://github.com/AndriiHeonia/hull/commit/9de6f9549b74fbb68bf4d5a449147b4c1d7cda0a
- https://github.com/AndriiHeonia/hull
