# [M] phpMyAdmin Arbitrary file read vulnerability

## Summary
Severity: Medium
Advisory: GHSA-c8wj-q36q-3wg4
CVE: CVE-2019-6799
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-c8wj-q36q-3wg4
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.8 <4.8.5

## Details
An issue was discovered in phpMyAdmin before 4.8.5. When the AllowArbitraryServer configuration setting is set to true, with the use of a rogue MySQL server, an attacker can read any file on the server that the web server's user can access. This is related to the mysql.allow_local_infile PHP configuration, and the inadvertent ignoring of "options(MYSQLI_OPT_LOCAL_INFILE" calls.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-6799
- https://github.com/phpmyadmin/composer
- https://lists.debian.org/debian-lts-announce/2019/02/msg00039.html
- https://www.phpmyadmin.net/security/PMASA-2019-1
- http://www.securityfocus.com/bid/106736
