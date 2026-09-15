# [C] Improper Input Validation in Symfony

## Summary
Severity: Critical
Advisory: GHSA-w4rc-rx25-8m86
CVE: CVE-2019-11325
CWE: CWE-116
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-02-12
Source: https://github.com/advisories/GHSA-w4rc-rx25-8m86
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected >=4.2.0 <4.2.12
- Packagist: `symfony/symfony` — affected >=4.3.0 <4.3.8
- Packagist: `symfony/var-exporter` — affected >=4.2.0 <4.2.12
- Packagist: `symfony/var-exporter` — affected >=4.3.0 <4.3.8

## Details
An issue was discovered in Symfony before 4.2.12 and 4.3.x before 4.3.8. The VarExport component incorrectly escapes strings, allowing some specially crafted ones to escalate to execution of arbitrary PHP code. This is related to symfony/var-exporter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11325
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2019-11325.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/var-exporter/CVE-2019-11325.yaml
- https://github.com/symfony/symfony/releases/tag/v4.3.8
- https://github.com/symfony/var-exporter/compare/d8bf442...57e00f3
- https://symfony.com/blog/cve-2019-11325-fix-escaping-of-strings-in-varexporter
- https://symfony.com/blog/symfony-4-3-8-released
- https://symfony.com/cve-2019-11325
