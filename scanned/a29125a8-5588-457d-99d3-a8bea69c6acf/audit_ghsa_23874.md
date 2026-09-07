# [M] phpMyAdmin allows remote attackers to obtain installation path via direct request for nonexistent file

## Summary
Severity: Medium
Advisory: GHSA-wcmm-28rg-mg3r
CVE: CVE-2011-0986
CWE: CWE-20, CWE-22
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-wcmm-28rg-mg3r
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=2.11.0 <2.11.11.2
- Packagist: `phpmyadmin/phpmyadmin` — affected >=3.3.0 <3.3.9.1

## Details
phpMyAdmin 2.11.x before 2.11.11.2, and 3.3.x before 3.3.9.1, does not properly handle the absence of the (1) README, (2) ChangeLog, and (3) LICENSE files, which allows remote attackers to obtain the installation path via a direct request for a nonexistent file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-0986
- https://exchange.xforce.ibmcloud.com/vulnerabilities/65424
- https://github.com/phpmyadmin/phpmyadmin
- http://lists.fedoraproject.org/pipermail/package-announce/2011-February/054349.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-February/054355.html
- http://phpmyadmin.git.sourceforge.net/git/gitweb.cgi?p=phpmyadmin/phpmyadmin%3Ba=commit%3Bh=035d002db1e1201e73e560d7d98591563b506a83
- http://phpmyadmin.git.sourceforge.net/git/gitweb.cgi?p=phpmyadmin/phpmyadmin;a=commit;h=035d002db1e1201e73e560d7d98591563b506a83
- http://www.mandriva.com/security/advisories?name=MDVSA-2011:026
- http://www.phpmyadmin.net/home_page/security/PMASA-2011-1.php
