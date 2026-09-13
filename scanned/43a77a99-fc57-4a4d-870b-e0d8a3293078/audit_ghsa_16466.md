# [C] Doctrine SQL injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-6q9v-4hq6-5m67
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-6q9v-4hq6-5m67
Type: github-advisory

## Affected
- Packagist: `doctrine/orm` — affected >=2.0.0 <2.0.3
- Packagist: `doctrine/orm` — affected >=1.0.0 <1.2.4

## Details
Doctrine is prone to SQL injection vulnerability. Users of Doctrine 1.2 and 2 should update to the newly released versions of both libraries immediately. Both versions only include the security fix and no other changes to their previous versions 1.2.3 and 2.0.2.

Affected versions are:
- 1.2.3 and earlier for PostgreSQL and DB2 Dialects
- 2.0.2 and earlier

The security issue was found to affect the `Doctrine\DBAL\Platforms\AbstractPlatform::modifyLimitQuery()` function which does not cast input values for limit and offset to integer and allows malicious SQL to be executed if these parameters are passed into Doctrine 2 directly from request variables without previous cast to integer. Functionality building on top using limit queries in the ORM such as `Doctrine\ORM\Query::setFirstResult()` and `Doctrine\ORM\Query::setMaxResults()` are also affected by this security issue.

The fix for this security issue breaks backwards compatibility for developers that extend the `Doctrine\DBAL\Platforms\AbstractPlatform::modifyLimitQuery()` method, because it is now marked as final. Please overwrite the `Doctrine\DBAL\Platforms\AbstractPlatform::doModifyLimitQuery()` method instead.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/doctrine/orm/2011-09-25.yaml
- https://github.com/doctrine/orm
- https://web.archive.org/web/20120315064147/https://www.doctrine-project.org/blog/doctrine-security-fix.html
