# [C] ADOdb Library SQL Injection

## Summary
Severity: Critical
Advisory: GHSA-3fj4-q72x-x2g9
CVE: CVE-2016-7405
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-3fj4-q72x-x2g9
Type: github-advisory

## Affected
- Packagist: `adodb/adodb-php` — affected >=5.0 <5.20.7

## Details
The `qstr` method in the PDO driver in the ADOdb Library for PHP before 5.x before 5.20.7 might allow remote attackers to conduct SQL injection attacks via vectors related to incorrect quoting.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-7405
- https://github.com/ADOdb/ADOdb/issues/226
- https://github.com/ADOdb/ADOdb/commit/bd9eca9f40220f9918ec3cc7ae9ef422b3e448b8
- https://github.com/ADOdb/ADOdb/blob/v5.20.7/docs/changelog.md
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LT3WU77BRUJREZUYQ3ZQBMUIVIVIND4Y
- https://security.gentoo.org/glsa/201701-59
- https://web.archive.org/web/20210123170727/http://www.securityfocus.com/bid/92969
- http://www.openwall.com/lists/oss-security/2016/09/07/8
- http://www.openwall.com/lists/oss-security/2016/09/15/1
