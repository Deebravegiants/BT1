# [M] Zend-developer-tools information disclosure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qg7m-mwxm-j3h7
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-qg7m-mwxm-j3h7
Type: github-advisory

## Affected
- Packagist: `zendframework/zend-developer-tools` — affected >=1.2.2 <1.2.3

## Details
The package zendframework/zend-developer-tools provides a web-based toolbar for introspecting an application. When updating the package to support PHP 7.3, a change was made that could potentially prevent toolbar entries that are enabled by default from being disabled.

## References
- https://github.com/zendframework/zend-developer-tools/commit/ce27f4624cf947bea2d746244b1ed6de10e22f1f
- https://framework.zend.com/security/advisory/ZF2019-01
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zend-developer-tools/ZF2019-01.yaml
- https://github.com/zendframework/zend-developer-tools
