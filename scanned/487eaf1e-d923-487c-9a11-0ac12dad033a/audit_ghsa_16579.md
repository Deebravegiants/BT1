# [M] Laravel Guard bypass in Eloquent models

## Summary
Severity: Medium
Advisory: GHSA-44pg-c29v-hp6r
CWE: CWE-20
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-44pg-c29v-hp6r
Type: github-advisory

## Affected
- Packagist: `laravel/framework` — affected >=5.5.0
- Packagist: `laravel/framework` — affected >=6.0.0 <6.18.34
- Packagist: `laravel/framework` — affected >=7.0.0 <7.23.2

## Details
In laravel releases before 6.18.34 and 7.23.2. It was possible to mass assign Eloquent attributes that included the model's table name:
```
$model->fill(['users.name' => 'Taylor']);
```
When doing so, Eloquent would remove the table name from the attribute for you. This was a "convenience" feature of Eloquent and was not documented.

However, when paired with validation, this can lead to unexpected and unvalidated values being saved to the database. For this reason, we have removed the automatic stripping of table names from mass-asignment operations so that the attributes go through the typical "fillable" / "guarded" logic. Any attributes containing table names that are not explicitly declared as fillable will be discarded.

This security release will be a breaking change for applications that were relying on the undocumented table name stripping during mass assignment. Since this feature was relatively unknown and undocumented, we expect the vast majority of Laravel applications to be able to upgrade without issues.

## References
- https://blog.laravel.com/security-release-laravel-61834-7232
- https://github.com/FriendsOfPHP/security-advisories/blob/master/laravel/framework/2020-08-06-1.yaml
- https://github.com/laravel/framework
