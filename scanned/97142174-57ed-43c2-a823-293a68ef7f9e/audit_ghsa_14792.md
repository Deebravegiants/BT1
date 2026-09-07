# [H] TYPO3 SQL Injection in dbal

## Summary
Severity: High
Advisory: GHSA-9895-53fc-98v2
Ecosystem: Packagist
Published: 2024-06-03
Source: https://github.com/advisories/GHSA-9895-53fc-98v2
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.18

## Details
A flaw in the database escaping API results in a SQL injection vulnerability when extension dbal is enabled and configured for MySQL passthrough mode in its extension configuration. All queries which use the DatabaseConnection::sql_query are vulnerable, even if arguments were properly escaped with DatabaseConnection::quoteStr beforehand.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2016-02-16-1.yaml
- https://typo3.org/article/typo3-core-sa-2016-001
