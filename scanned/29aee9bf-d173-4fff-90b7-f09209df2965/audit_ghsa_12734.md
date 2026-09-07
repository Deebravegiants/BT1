# [M] CakePHP vulnerable to Cross-site Scripting in some development error pages

## Summary
Severity: Medium
Advisory: GHSA-xwhj-pqcg-8rcr
Ecosystem: Packagist
Published: 2023-01-20
Source: https://github.com/advisories/GHSA-xwhj-pqcg-8rcr
Type: github-advisory

## Affected
- Packagist: `cakephp/cakephp` — affected >=3.4.0 <3.4.14
- Packagist: `cakephp/cakephp` — affected >=3.5.0 <3.5.17
- Packagist: `cakephp/cakephp` — affected >=3.6.0 <3.6.4

## Details
CakePHP 3.4 prior to 3.4.14, 3.5 prior to 3.5.17, and 3.6 prior to 3.6.4 contains a cross-site-scripting (XSS) vulnerability in the development only `missing route` and `duplicate named route` error pages.

## References
- https://github.com/cakephp/cakephp/commit/1ea0c87de729e0dcd53eb6fe3bc86ba739121d8e
- https://bakery.cakephp.org/2018/05/20/cakephp_364_3517_3414_released.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/cakephp/cakephp/2018-05-20.yaml
- https://github.com/cakephp/cakephp
