# [C] Propel2 SQL injection possible with limit() on MySQL

## Summary
Severity: Critical
Advisory: GHSA-7vw7-qx38-37vr
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-20
Source: https://github.com/advisories/GHSA-7vw7-qx38-37vr
Type: github-advisory

## Affected
- Packagist: `propel/propel` — affected >=2.0.0-alpha1 <2.0.0-alpha8

## Details
The limit() query method is susceptible to catastrophic SQL injection with MySQL.

For example, given a model User for a table users:
```
UserQuery::create()->limit('1;DROP TABLE users')->find();
```
This will drop the users table!

The cause appears to be a lack of integer casting of the limit input in either Propel\Runtime\ActiveQuery\Criteria::setLimit() or in Propel\Runtime\Adapter\Pdo\MysqlAdapter::applyLimit(). The code comments there seem to imply that casting was avoided due to overflow issues with 32-bit integers.

This is surprising behavior since one of the primary purposes of an ORM is to prevent basic SQL injection.

This affects all versions of Propel: 1.x, 2.x, and 3.

## References
- https://github.com/propelorm/Propel2/issues/1463
- https://github.com/propelorm/Propel2/pull/1464
- https://github.com/propelorm/Propel2/commit/cd23d7384a15cfe203e23b3a835c8ab1d81d9246
- https://github.com/FriendsOfPHP/security-advisories/blob/master/propel/propel/2018-02-14.yaml
- https://github.com/propelorm/Propel2
