# [H] phpMyAdmin HTTP Response Splitting Vulnerability

## Summary
Severity: High
Advisory: GHSA-xrpq-63mp-9vcw
CVE: CVE-2009-1149
CWE: CWE-113, CWE-20
Ecosystem: Packagist
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-xrpq-63mp-9vcw
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=0 <3.1.3.1

## Details
CRLF injection vulnerability in `bs_disp_as_mime_type.php` in the BLOB streaming feature in phpMyAdmin before 3.1.3.1 allows remote attackers to inject arbitrary HTTP headers and conduct HTTP response splitting attacks via the (1) `c_type` and possibly (2) `file_type` parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-1149
- https://github.com/phpmyadmin/phpmyadmin/commit/69bfbf11c7e9487dfa96293aaa797ff14bb513f0
- https://github.com/phpmyadmin/composer
- http://lists.opensuse.org/opensuse-security-announce/2009-04/msg00003.html
- http://phpmyadmin.svn.sourceforge.net/viewvc/phpmyadmin/branches/MAINT_3_1_3/phpMyAdmin/bs_disp_as_mime_type.php?r1=12303&r2=12302&pathrev=12303
- http://www.phpmyadmin.net/home_page/security/PMASA-2009-1.php
