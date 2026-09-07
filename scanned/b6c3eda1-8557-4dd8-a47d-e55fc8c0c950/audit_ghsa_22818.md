# [M] phpMyAdmin remote variable manipulation

## Summary
Severity: Medium
Advisory: GHSA-vqcm-r62w-w437
CVE: CVE-2011-2505
CWE: CWE-94
Ecosystem: Packagist
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-vqcm-r62w-w437
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=3.0 <3.3.10.2
- Packagist: `phpmyadmin/phpmyadmin` — affected >=3.4 <3.4.3.1

## Details
`libraries/auth/swekey/swekey.auth.lib.php` in the Swekey authentication feature in phpMyAdmin 3.x before 3.3.10.2 and 3.4.x before 3.4.3.1 assigns values to arbitrary parameters referenced in the query string, which allows remote attackers to modify the `SESSION` superglobal array via a crafted request, related to a "remote variable manipulation vulnerability."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-2505
- https://github.com/phpmyadmin/composer/commit/7ebd958b2bf59f96fecd5b3322bdbd0b244a7967
- https://github.com/phpmyadmin/phpmyadmin/commit/6e6e129f26295c83d67b74e202628a4b8bc49e54
- https://github.com/phpmyadmin/phpmyadmin/commit/7ebd958b2bf59f96fecd5b3322bdbd0b244a7967
- https://github.com/phpmyadmin/composer
- https://web.archive.org/web/20110712103138/http://www.xxor.se/advisories/phpMyAdmin_3.x_Multiple_Remote_Code_Executions.txt
- https://web.archive.org/web/20111116172111/http://www.securityfocus.com/archive/1/518804/100/0/threaded
- https://web.archive.org/web/20121105034518/http://www.mandriva.com/en/support/security/advisories?name=MDVSA-2011:124
- http://ha.xxor.se/2011/07/phpmyadmin-3x-multiple-remote-code.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-July/062719.html
- http://securityreason.com/securityalert/8306
- http://typo3.org/teams/security/security-bulletins/typo3-sa-2011-008
- http://www.debian.org/security/2011/dsa-2286
- http://www.exploit-db.com/exploits/17514
- http://www.openwall.com/lists/oss-security/2011/06/28/2
- http://www.openwall.com/lists/oss-security/2011/06/28/6
- http://www.openwall.com/lists/oss-security/2011/06/28/8
- http://www.openwall.com/lists/oss-security/2011/06/29/11
- http://www.phpmyadmin.net/home_page/security/PMASA-2011-5.php
