# [H] Query Binding Exploitation

## Summary
Severity: High
Advisory: GHSA-3p32-j457-pg5x
CVE: CVE-2021-21263
CWE: CWE-74, CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-01-19
Source: https://github.com/advisories/GHSA-3p32-j457-pg5x
Type: github-advisory

## Affected
- Packagist: `laravel/framework` — affected >=8.0.0 <8.22.1
- Packagist: `illuminate/database` — affected >=7.0.0 <7.30.3
- Packagist: `illuminate/database` — affected >=8.0.0 <8.22.1
- Packagist: `illuminate/database` — affected >=6.0.0 <6.20.12
- Packagist: `laravel/framework` — affected >=6.0.0 <6.20.11
- Packagist: `laravel/framework` — affected >=7.0.0 <7.30.2

## Details
### Description

Laravel versions <6.20.12, <7.30.3 & <8.22.1 contain a query binding exploitation.

If a request is crafted where a field that is normally a non-array value is an array, and that input is not validated or cast to its expected type before being passed to the query builder, an unexpected number of query bindings can be added to the query. In some situations, this will simply lead to no results being returned by the query builder; however, it is possible certain queries could be affected in a way that causes the query to return unexpected results.

This vulnerability was discovered by Tim Groenevelt (tim.g@foodbyus.com).

### References

- https://github.com/laravel/framework/pull/35865

## References
- https://github.com/laravel/framework/security/advisories/GHSA-3p32-j457-pg5x
- https://nvd.nist.gov/vuln/detail/CVE-2021-21263
- https://github.com/laravel/framework/pull/35865
- https://blog.laravel.com/security-laravel-62011-7302-8221-released
- https://blog.laravel.com/security-laravel-62012-7303-released
- https://github.com/FriendsOfPHP/security-advisories/blob/master/illuminate/database/CVE-2021-21263.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/laravel/framework/CVE-2021-21263.yaml
- https://packagist.org/packages/illuminate/database
- https://packagist.org/packages/laravel/framework
