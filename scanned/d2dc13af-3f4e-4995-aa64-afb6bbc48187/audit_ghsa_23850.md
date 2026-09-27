# [C] ThinkPHP SQLi Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-78q9-24gv-g288
CVE: CVE-2018-18529
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-78q9-24gv-g288
Type: github-advisory

## Affected
- Packagist: `topthink/framework` — affected >=0

## Details
ThinkPHP 3.2.4 has SQL Injection via the count parameter because the `Library/Think/Db/Driver/Mysql.class.php` `parseKey` function mishandles the key variable. NOTE: a backquote character is not required in the attack URI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18529
- https://www.kingkk.com/2018/10/Thinkphp-%E8%81%9A%E5%90%88%E6%9F%A5%E8%AF%A2%E6%BC%8F%E6%B4%9E/#ThinkPHP3-lt-3-2-4
