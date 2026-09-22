# [C] ZendFramework1 Potential SQL injection in the ORDER implementation of Zend_Db_Select

## Summary
Severity: Critical
Advisory: GHSA-2x36-qhx3-7m5f
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-2x36-qhx3-7m5f
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework1` — affected >=1.12.0 <1.12.7

## Details
The implementation of the ORDER BY SQL statement in Zend_Db_Select of Zend Framework 1 contains a potential SQL injection when the query string passed contains parentheses.

For instance, the following code is affected by this issue:
```
$db     = Zend_Db::factory( /* options here */ );
$select = $db->select()
    ->from(array('p' => 'products'))
    ->order('MD5(1); drop table products');
echo $select;
```
This code produce the string:
```
SELECT "p".* FROM "products" AS "p" ORDER BY MD5(1);drop table products ASC
```
instead of the correct one:
```
SELECT "p".* FROM "products" AS "p" ORDER BY "MD5(1);drop table products" ASC
```
The SQL injection occurs because we create a new Zend_Db_Expr() object, in presence of parentheses, passing directly the value without any filter on the string.

## References
- https://framework.zend.com/security/advisory/ZF2014-04
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework1/ZF2014-04.yaml
- https://github.com/zendframework/zf1
