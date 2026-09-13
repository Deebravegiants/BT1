# [H] Unexpected database bindings

## Summary
Severity: High
Advisory: GHSA-x7p5-p2c9-phvg
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-02-02
Source: https://github.com/advisories/GHSA-x7p5-p2c9-phvg
Type: github-advisory

## Affected
- Packagist: `laravel/framework` — affected >=0 <6.20.14
- Packagist: `laravel/framework` — affected >=7.0.0 <7.30.4
- Packagist: `laravel/framework` — affected >=8.0.0 <8.24.0
- Packagist: `illuminate/database` — affected >=0 <6.20.14
- Packagist: `illuminate/database` — affected >=7.0.0 <7.30.4
- Packagist: `illuminate/database` — affected >=8.0.0 <8.24.0

## Details
This is a follow-up to the previous security advisory (GHSA-3p32-j457-pg5x) which addresses a few additional edge cases.

If a request is crafted where a field that is normally a non-array value is an array, and that input is not validated or cast to its expected type before being passed to the query builder, an unexpected number of query bindings can be added to the query. In some situations, this will simply lead to no results being returned by the query builder; however, it is possible certain queries could be affected in a way that causes the query to return unexpected results.

## References
- https://github.com/laravel/framework/security/advisories/GHSA-x7p5-p2c9-phvg
- https://github.com/advisories/GHSA-3p32-j457-pg5x
- https://packagist.org/packages/illuminate/database
- https://packagist.org/packages/laravel/framework
