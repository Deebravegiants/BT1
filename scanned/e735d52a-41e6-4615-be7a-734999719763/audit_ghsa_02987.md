# [M] CSV Injection in symfony/serializer

## Summary
Severity: Medium
Advisory: GHSA-2xhg-w2g5-w95x
CVE: CVE-2021-41270
CWE: CWE-1236
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-11-24
Source: https://github.com/advisories/GHSA-2xhg-w2g5-w95x
Type: github-advisory

## Affected
- Packagist: `symfony/serializer` — affected >=5.0.0 <5.3.12
- Packagist: `symfony/serializer` — affected >=4.1.0 <4.4.35
- Packagist: `symfony/symfony` — affected >=4.1.0 <4.4.35
- Packagist: `symfony/symfony` — affected >=5.0.0 <5.3.12

## Details
Description
-----------

CSV Injection, also known as Formula Injection, occurs when websites embed untrusted input inside CSV files. When a spreadsheet program opens a CSV, any cell starting with `=` is interpreted by the software as a formula and could be abused by an attacker.

In Symfony 4.1, we've added the opt-in `csv_escape_formulas` option in `CsvEncoder`, to prefix all cells starting by  `=`, `+`, `-` or `@` by a tab `\t`. 

Since then, OWASP added 2 chars in that list: 
- Tab (0x09)
- Carriage return (0x0D)

This makes our previous prefix char (Tab `\t`) part of the vulnerable characters, and [OWASP suggests](https://owasp.org/www-community/attacks/CSV_Injection) using the single quote `'` for prefixing the value.

Resolution
----------

Symfony now follows the OWASP recommendations and use the single quote `'` to prefix formulas and adds the prefix to cells starting by `\t`, `\r` as well as `=`, `+`, `-` and `@`.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/3da6f2d45e7536ccb2a26f52fbaf340917e208a8) for branch 4.4.

Credits
-------

We would like to thank Jake Barwell for reporting the issue and Jérémy Derussé for fixing the issue.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-2xhg-w2g5-w95x
- https://nvd.nist.gov/vuln/detail/CVE-2021-41270
- https://github.com/symfony/symfony/pull/44243
- https://github.com/symfony/symfony/commit/3da6f2d45e7536ccb2a26f52fbaf340917e208a8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/serializer/CVE-2021-41270.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2021-41270.yaml
- https://github.com/symfony/symfony
- https://github.com/symfony/symfony/releases/tag/v5.3.12
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3BPT4SF6SIXFMZARDWED5T32J7JEH3EP
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QSREFD2TJT5LWKM6S4MD3W26NQQ5WJUP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3BPT4SF6SIXFMZARDWED5T32J7JEH3EP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QSREFD2TJT5LWKM6S4MD3W26NQQ5WJUP
- https://symfony.com/cve-2021-41270
