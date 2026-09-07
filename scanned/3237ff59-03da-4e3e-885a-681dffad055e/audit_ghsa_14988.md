# [C] Zendframework1 Potential SQL injection in ORDER and GROUP functions

## Summary
Severity: Critical
Advisory: GHSA-6fqw-j3vm-7f66
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-6fqw-j3vm-7f66
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework1` — affected >=0 <1.12.20

## Details
The implementation of ORDER BY and GROUP BY in Zend_Db_Select remained prone to SQL injection when a combination of SQL expressions and comments were used. This security patch provides a comprehensive solution that identifies and removes comments prior to checking validity of the statement to ensure no SQLi vectors occur.

The implementation of ORDER BY and GROUP BY in Zend_Db_Select of ZF1 is vulnerable by the following SQL injection:
```
$db = Zend_Db::factory(/* options here */);
$select = new Zend_Db_Select($db);
$select->from('p');
$select->order("MD5(\"a(\");DELETE FROM p2; #)"); // same with group()
```
The above $select will render the following SQL statement:
```
SELECT `p`.* FROM `p` ORDER BY MD5("a(");DELETE FROM p2; #) ASC
```
instead of the correct one:
```
SELECT "p".* FROM "p" ORDER BY "MD5(""a("");DELETE FROM p2; #)" ASC
```
This security fix can be considered an improvement of the previous ZF2016-02 and ZF2014-04 advisories.

As a final consideration, we recommend developers either never use user input for these operations, or filter user input thoroughly prior to invoking Zend_Db. You can use the Zend_Db_Select::quoteInto() method to filter the input data, as shown in this example:
```
$db    = Zend_Db::factory(...);
$input = "MD5(\"a(\");DELETE FROM p2; #)"; // user input can be an attack
$order = $db->quoteInto("SQL statement for ORDER", $input);

$select = new Zend_Db_Select($db);
$select->from('p');
$select->order($order); // same with group()
```

## References
- https://framework.zend.com/security/advisory/ZF2016-03
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework1/ZF2016-03.yaml
- https://github.com/zendframework/zf1
