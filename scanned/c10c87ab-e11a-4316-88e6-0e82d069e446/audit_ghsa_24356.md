# [C] phpMyAdmin Code Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-rv57-479x-x4qv
CVE: CVE-2016-5734
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-rv57-479x-x4qv
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0.10.0 <4.0.10.16
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4.15.0 <4.4.15.7
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6.0 <4.6.3

## Details
phpMyAdmin 4.0.x before 4.0.10.16, 4.4.x before 4.4.15.7, and 4.6.x before 4.6.3 does not properly choose delimiters to prevent use of the preg_replace e (aka eval) modifier, which might allow remote attackers to execute arbitrary PHP code via a crafted string, as demonstrated by the table search-and-replace implementation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5734
- https://github.com/phpmyadmin/phpmyadmin/commit/1cc7466db3a05e95fe57a6702f41773e6829d54b
- https://github.com/phpmyadmin/phpmyadmin/commit/4bcc606225f15bac0b07780e74f667f6ac283da7
- https://github.com/phpmyadmin/phpmyadmin
- https://security.gentoo.org/glsa/201701-32
- https://web.archive.org/web/20200227223418/http://www.securityfocus.com/bid/91387
- https://www.exploit-db.com/exploits/40185
- https://www.phpmyadmin.net/security/PMASA-2016-27
