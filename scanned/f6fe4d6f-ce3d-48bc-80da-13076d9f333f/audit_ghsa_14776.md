# [H] ZendFramework SQL injection due to execution of platform-specific SQL containing interpolations

## Summary
Severity: High
Advisory: GHSA-x2f4-8wxf-w3vf
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-x2f4-8wxf-w3vf
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework` — affected >=2.0.0 <2.0.8
- Packagist: `zendframework/zendframework` — affected >=2.1.0 <2.1.4

## Details
The `Zend\Db` component in Zend Framework 2 provides platform abstraction, which is used in particular for SQL abstraction. Two methods defined in the platform interface, `quoteValue()` and `quoteValueList()`, allow users to manually quote values for creating SQL statements; these are in turn consumed by aspects of the SQL abstraction platform, including `Zend\Db\Sql\Sql::getSqlStringForSqlObject()`, and the `getSqlString()` method provided in a number of classes in the Zend\Db\Sql namespace.

While these methods are primarily intended for debugging and logging purposes, developers can use them to produce SQL that is then passed to the driver to execute. Due to a flaw in how the `quoteValue()` and `quoteValueList()` methods were written, this can lead to potential SQL injection.

The offending code is located in any of the `Zend\Db\Adapter\Platform*` objects, particularly the quoteValue() and `quoteValueList()` methods. These methods did not take into account most of the possible escapable characters that would need to be escaped when attempting to create a quoted value for interpolation into a SQL string. Moreover, these methods did value quoting without extension level coordination which, when available, takes character-sets into account when quoting.

## References
- https://github.com/zendframework/zendframework/commit/0ef63e7db5fa30a79a58eb7c6466c6ab5c0618c5
- https://github.com/zendframework/zendframework/commit/546074660e6e10b9191bf0dc62b524d99f71a5cd
- https://github.com/zendframework/zendframework/commit/6d83777786b8e6171d82191ef917afd09fcb6601
- https://github.com/zendframework/zendframework/commit/870741d0c01a24ff23f9e209c8d393bd3a4115e3
- https://github.com/zendframework/zendframework/commit/95c88c236e80b475141d227bdf7866ca40287dd1
- https://github.com/zendframework/zendframework/commit/d1f259b9d6dbd7c3828360afcfdd3658f2163ea0
- https://framework.zend.com/security/advisory/ZF2013-03
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework/ZF2013-03.yaml
- https://github.com/zendframework/zendframework
