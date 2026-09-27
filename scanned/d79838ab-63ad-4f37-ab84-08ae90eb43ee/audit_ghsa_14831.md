# [C] ZendFramework potential SQL Injection Vector When Using PDO_MySql

## Summary
Severity: Critical
Advisory: GHSA-qf36-fx9f-232x
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-qf36-fx9f-232x
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework1` — affected >=1.10.0 <1.10.9
- Packagist: `zendframework/zendframework1` — affected >=1.11.0 <1.11.6

## Details
Developers using non-ASCII-compatible encodings in conjunction with the MySQL PDO driver of PHP may be vulnerable to SQL injection attacks. Developers using ASCII-compatible encodings like UTF8 or latin1 are not affected by this PHP issue, which is described in more detail here:

http://bugs.php.net/bug.php?id=47802
The PHP Group included a feature in PHP 5.3.6+ that allows any character set information to be passed as part of the DSN in PDO to allow both the database as well as the C-level driver to be aware of which charset is in use which is of special importance when PDO's quoting mechanisms are utilized, which Zend Framework also relies on.

## References
- https://framework.zend.com/security/advisory/ZF2011-02
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework1/ZF2011-02.yaml
- https://github.com/zendframework/zf1
- http://bugs.php.net/bug.php?id=47802
