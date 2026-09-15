# [M] Laravel Risk of mass-assignment vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-cc2w-ghc5-m5qr
CWE: CWE-20
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-cc2w-ghc5-m5qr
Type: github-advisory

## Affected
- Packagist: `illuminate/database` — affected >=4.0.0 <4.1.29

## Details
Laravel 4.1.29 improves the column quoting for all database drivers. This protects your application from some mass assignment vulnerabilities when not using the fillable property on models. If you are using the fillable property on your models to protect against mass assignment, your application is not vulnerable. However, if you are using guarded and are passing a user controlled array into an "update" or "save" type function, you should upgrade to 4.1.29 immediately as your application may be at risk of mass assignment.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/illuminate/database/2014-05-20.yaml
- https://github.com/illuminate/database
- https://laravel.com/docs/5.1/upgrade#upgrade-4.1.29
