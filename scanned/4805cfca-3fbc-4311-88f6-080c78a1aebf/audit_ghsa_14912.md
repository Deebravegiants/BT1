# [C] Zendframework1 potential SQL injection vector using null byte for PDO (MsSql, SQLite)

## Summary
Severity: Critical
Advisory: GHSA-v42g-7q2x-cw32
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-v42g-7q2x-cw32
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework1` — affected >=1.12.0 <1.12.16

## Details
The PDO adapters of Zend Framework 1 do not filter null bytes values in SQL statements. A PDO adapter can treat null bytes in a query as a string terminator, allowing an attacker to add arbitrary SQL following a null byte, and thus create a SQL injection.

We tested and verified the null byte injection using pdo_dblib (FreeTDS) on a Linux environment to access a remote Microsoft SQL Server, and also tested against and noted the vector against pdo_sqlite.

## References
- https://framework.zend.com/security/advisory/ZF2015-08
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework1/ZF2015-08.yaml
- https://github.com/zendframework/zf1
