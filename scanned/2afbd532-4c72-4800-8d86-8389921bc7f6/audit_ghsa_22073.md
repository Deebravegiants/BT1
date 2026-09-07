# [H] phpMyAdmin vulnerable to static code injection

## Summary
Severity: High
Advisory: GHSA-p6h7-29r2-g88f
CVE: CVE-2011-2506
CWE: CWE-94
Ecosystem: Packagist
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-p6h7-29r2-g88f
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=3.0 <3.3.10.2
- Packagist: `phpmyadmin/phpmyadmin` — affected >=3.4 <3.4.3.1

## Details
`setup/lib/ConfigGenerator.class.php` in phpMyAdmin 3.x before 3.3.10.2 and 3.4.x before 3.4.3.1 does not properly restrict the presence of comment closing delimiters, which allows remote attackers to conduct static code injection attacks by leveraging the ability to modify the SESSION superglobal array.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-2506
- https://github.com/phpmyadmin/phpmyadmin/commit/0fbedaf5fd7a771d0885c6b7385d934fc90d0d7f
- https://github.com/phpmyadmin/phpmyadmin/commit/2e01647949df937040e73a94ce0bac0daecbdcf4
- https://github.com/phpmyadmin/composer
- https://web.archive.org/web/20110712103138/http://www.xxor.se/advisories/phpMyAdmin_3.x_Multiple_Remote_Code_Executions.txt
- https://web.archive.org/web/20111116172111/http://www.securityfocus.com/archive/1/518804/100/0/threaded
- https://web.archive.org/web/20121105034518/http://www.mandriva.com/en/support/security/advisories?name=MDVSA-2011:124
- http://ha.xxor.se/2011/07/phpmyadmin-3x-multiple-remote-code.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-July/062719.html
- http://phpmyadmin.git.sourceforge.net/git/gitweb.cgi?p=phpmyadmin/phpmyadmin;a=commit;h=0fbedaf5fd7a771d0885c6b7385d934fc90d0d7f
- http://securityreason.com/securityalert/8306
- http://typo3.org/teams/security/security-bulletins/typo3-sa-2011-008
- http://www.debian.org/security/2011/dsa-2286
- http://www.exploit-db.com/exploits/17514
- http://www.openwall.com/lists/oss-security/2011/06/28/2
- http://www.openwall.com/lists/oss-security/2011/06/28/6
- http://www.openwall.com/lists/oss-security/2011/06/28/8
- http://www.openwall.com/lists/oss-security/2011/06/29/11
- http://www.phpmyadmin.net/home_page/security/PMASA-2011-6.php
