# [C] propel/propel1 SQL injection possible with limit() on MySQL

## Summary
Severity: Critical
Advisory: GHSA-7g7c-qhf3-x59p
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-20
Source: https://github.com/advisories/GHSA-7g7c-qhf3-x59p
Type: github-advisory

## Affected
- Packagist: `propel/propel1` — affected >=1 <1.7.2

## Details
The limit() query method is susceptible to catastrophic SQL injection with MySQL.

For example, given a model User for a table users:
```
UserQuery::create()->limit('1;DROP TABLE users')->find();
```
This will drop the users table!

The cause appears to be a lack of integer casting of the limit input in either Criteria::setLimit() or in DBMySQL::applyLimit(). The code comments there seem to imply that casting was avoided due to overflow issues with 32-bit integers.

This is surprising behavior since one of the primary purposes of an ORM is to prevent basic SQL injection.

This affects all versions of Propel: 1.x, 2.x, and 3.

## References
- https://github.com/propelorm/Propel/issues/1052
- https://github.com/propelorm/Propel/pull/1054
- https://github.com/propelorm/Propel/commit/b72093201f8e225410f62a246653ac039e31c90a
- https://github.com/FriendsOfPHP/security-advisories/blob/master/propel/propel1/2018-02-14.yaml
- https://github.com/propelorm/Propel
