# [H] laravel framework Unexpected database bindings via requests

## Summary
Severity: High
Advisory: GHSA-jwvj-pwww-3mj5
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-jwvj-pwww-3mj5
Type: github-advisory

## Affected
- Packagist: `laravel/framework` — affected >=6.0.0 <6.20.14
- Packagist: `laravel/framework` — affected >=7.0.0 <7.30.4
- Packagist: `laravel/framework` — affected >=8.0.0 <8.24.0

## Details
This is a follow-up to the security advisory https://github.com/laravel/framework/security/advisories/GHSA-3p32-j457-pg5x which addresses a few additional edge cases.

If a request is crafted where a field that is normally a non-array value is an array, and that input is not validated or cast to its expected type before being passed to the query builder, an unexpected number of query bindings can be added to the query. In some situations, this will simply lead to no results being returned by the query builder; however, it is possible certain queries could be affected in a way that causes the query to return unexpected results.

## References
- https://github.com/laravel/framework/security/advisories/GHSA-x7p5-p2c9-phvg
- https://github.com/FriendsOfPHP/security-advisories/blob/master/laravel/framework/2021-01-21.yaml
- https://github.com/laravel/framework
