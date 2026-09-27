# [C] Sabberworm PHP CSS Parser Code injection vulnerability in allSelectors()

## Summary
Severity: Critical
Advisory: GHSA-phrq-v4q2-hmq6
CVE: CVE-2020-13756
CWE: CWE-20, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-26
Source: https://github.com/advisories/GHSA-phrq-v4q2-hmq6
Type: github-advisory

## Affected
- Packagist: `sabberworm/php-css-parser` — affected >=8.3.0 <8.3.1
- Packagist: `sabberworm/php-css-parser` — affected >=8.2.0 <8.2.1
- Packagist: `sabberworm/php-css-parser` — affected >=8.1.0 <8.1.1
- Packagist: `sabberworm/php-css-parser` — affected >=8.0.0 <8.0.1
- Packagist: `sabberworm/php-css-parser` — affected >=7.0.0 <7.0.4
- Packagist: `sabberworm/php-css-parser` — affected >=6.0.0 <6.0.2
- Packagist: `sabberworm/php-css-parser` — affected >=5.2.0 <5.2.1
- Packagist: `sabberworm/php-css-parser` — affected >=5.1.0 <5.1.3
- Packagist: `sabberworm/php-css-parser` — affected >=5.0.0 <5.0.9
- Packagist: `sabberworm/php-css-parser` — affected >=4.0.0 <4.0.1
- Packagist: `sabberworm/php-css-parser` — affected >=3.0.0 <3.0.1
- Packagist: `sabberworm/php-css-parser` — affected >=2.0.0 <2.0.1
- Packagist: `sabberworm/php-css-parser` — affected >=1.0.0 <1.0.1

## Details
Sabberworm PHP CSS Parser before 8.3.1 calls eval on uncontrolled data, possibly leading to remote code execution if the function allSelectors() or getSelectorsBySpecificity() is called with input from an attacker.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13756
- https://github.com/sabberworm/PHP-CSS-Parser/commit/2ebf59e8bfbf6cfc1653a5f0ed743b95062c62a4
- https://github.com/FriendsOfPHP/security-advisories/blob/master/sabberworm/php-css-parser/CVE-2020-13756.yaml
- https://github.com/sabberworm/PHP-CSS-Parser/releases/tag/8.3.1
- https://lists.debian.org/debian-lts-announce/2025/10/msg00013.html
- https://packetstormsecurity.com/files/cve/CVE-2020-13756
- http://packetstormsecurity.com/files/157923/Sabberworm-PHP-CSS-Code-Injection.html
- http://seclists.org/fulldisclosure/2020/Jun/7
