# [C] ThinkPHP SQLi Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-j7g8-3qqg-8cvm
CVE: CVE-2018-18546
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-j7g8-3qqg-8cvm
Type: github-advisory

## Affected
- Packagist: `topthink/framework` — affected >=0

## Details
ThinkPHP 3.2.4 has SQL Injection via the order parameter because the `Library/Think/Db/Driver.class.php` parseOrder function mishandles the key variable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18546
- https://github.com/top-think/framework/issues/2613
- https://github.com/top-think/thinkphp/commit/9748cb80d2f24c89218f358ca2f5ab88ee33396f
- https://98587329.github.io/2018/10/09/thinkphp%E6%B3%A8%E5%85%A5%E5%88%86%E6%9E%90
