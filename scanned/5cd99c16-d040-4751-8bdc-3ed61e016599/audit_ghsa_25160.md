# [H] phpMyAdmin allows remote attackers to bypass authentication and obtain sensitive information

## Summary
Severity: High
Advisory: GHSA-gmc7-jvv7-w245
CVE: CVE-2010-4481
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-gmc7-jvv7-w245
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=0 <3.4.0-beta1

## Details
phpMyAdmin before 3.4.0-beta1 allows remote attackers to bypass authentication and obtain sensitive information via a direct request to phpinfo.php, which calls the phpinfo function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-4481
- https://github.com/phpmyadmin/phpmyadmin
- http://phpmyadmin.git.sourceforge.net/git/gitweb.cgi?p=phpmyadmin/phpmyadmin%3Ba=commitdiff%3Bh=4d9fd005671b05c4d74615d5939ed45e4d019e4c
- http://phpmyadmin.git.sourceforge.net/git/gitweb.cgi?p=phpmyadmin/phpmyadmin;a=commitdiff;h=4d9fd005671b05c4d74615d5939ed45e4d019e4c
- http://www.debian.org/security/2010/dsa-2139
- http://www.mandriva.com/security/advisories?name=MDVSA-2011:000
- http://www.phpmyadmin.net/home_page/security/PMASA-2010-10.php
