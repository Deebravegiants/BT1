# [H] SQL Server LIMIT / OFFSET SQL Injection in laravel/framework and illuminate/database

## Summary
Severity: High
Advisory: GHSA-4mg9-vhxq-vm7j
CWE: CWE-89
Ecosystem: Packagist
Published: 2021-04-29
Source: https://github.com/advisories/GHSA-4mg9-vhxq-vm7j
Type: github-advisory

## Affected
- Packagist: `laravel/framework` — affected >=8.0.0 <8.40.0
- Packagist: `laravel/framework` — affected >=0 <6.20.26
- Packagist: `illuminate/database` — affected >=8.0.0 <8.40.0
- Packagist: `illuminate/database` — affected >=0 <6.20.26

## Details
### Impact

Those using SQL Server with Laravel and allowing user input to be passed directly to the `limit` and `offset` functions are vulnerable to SQL injection. Other database drivers such as MySQL and Postgres are not affected by this vulnerability.

### Patches

This problem has been patched on Laravel versions 6.20.26, 7.30.5, and 8.40.0.

### Workarounds

You may workaround this vulnerability by ensuring that only integers are passed to the `limit` and `offset` functions, as well as the `skip` and `take` functions.

## References
- https://github.com/laravel/framework/security/advisories/GHSA-4mg9-vhxq-vm7j
- https://github.com/laravel/framework
- https://packagist.org/packages/illuminate/database
- https://packagist.org/packages/laravel/framework
