# [H] BIT-laravel-2020-24940

## Summary
Severity: High
Advisory: BIT-laravel-2020-24940
Aliases: CVE-2020-24940, GHSA-c7rm-w2hj-x8g3
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-laravel-2020-24940
Type: osv

## Affected
- Bitnami: `laravel` — affected >=7.0.0 <7.23.2

## Details
An issue was discovered in Laravel before 6.18.34 and 7.x before 7.23.2. Unvalidated values are saved to the database in some situations in which table names are stripped during a mass assignment.

## References
- https://blog.laravel.com/security-release-laravel-61834-7232
- https://nvd.nist.gov/vuln/detail/CVE-2020-24940
