# [M] phpMyAdmin Directory Traversal Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-xhqq-554j-p4x8
CVE: CVE-2011-2718
CWE: CWE-22
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-xhqq-554j-p4x8
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=3.4 <3.4.3.2

## Details
Multiple directory traversal vulnerabilities in the relational schema implementation in phpMyAdmin 3.4.x before 3.4.3.2 allow remote authenticated users to include and execute arbitrary local files via directory traversal sequences in an export type field, related to (1) `libraries/schema/User_Schema.class.php` and (2) `schema_export.php`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-2718
- https://github.com/phpmyadmin/phpmyadmin/commit/3ae58f0cd6b89ad4767920f9b214c38d3f6d4393
- https://bugzilla.redhat.com/show_bug.cgi?id=725383
- https://exchange.xforce.ibmcloud.com/vulnerabilities/68768
- https://github.com/phpmyadmin/composer
- https://web.archive.org/web/20120111084137/http://www.securityfocus.com/bid/48874
- https://web.archive.org/web/20121105034518/http://www.mandriva.com/en/support/security/advisories?name=MDVSA-2011:124
- http://lists.fedoraproject.org/pipermail/package-announce/2011-August/063410.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-August/063418.html
- http://phpmyadmin.git.sourceforge.net/git/gitweb.cgi?p=phpmyadmin/phpmyadmin%3Ba=commit%3Bh=3ae58f0cd6b89ad4767920f9b214c38d3f6d4393
- http://phpmyadmin.git.sourceforge.net/git/gitweb.cgi?p=phpmyadmin/phpmyadmin;a=commit;h=3ae58f0cd6b89ad4767920f9b214c38d3f6d4393
- http://www.openwall.com/lists/oss-security/2011/07/25/4
- http://www.openwall.com/lists/oss-security/2011/07/26/10
- http://www.phpmyadmin.net/home_page/security/PMASA-2011-11.php
