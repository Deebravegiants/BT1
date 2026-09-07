# [H] phpMyAdmin unsafely handles temporary files

## Summary
Severity: High
Advisory: GHSA-9645-6g72-2pv8
CVE: CVE-2008-7252
CWE: CWE-377
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9645-6g72-2pv8
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=2.11.0 <2.11.10

## Details
`libraries/File.class.php` in phpMyAdmin 2.11.x before 2.11.10 uses predictable filenames for temporary files, which has unknown impact and attack vectors.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-7252
- https://github.com/phpmyadmin/composer
- https://web.archive.org/web/20100613071447/http://secunia.com/advisories/38211
- https://web.archive.org/web/20100613071509/http://secunia.com/advisories/39503
- https://web.archive.org/web/20110729050522/http://www.securityfocus.com/bid/37826
- http://lists.opensuse.org/opensuse-security-announce/2010-01/msg00007.html
- http://phpmyadmin.svn.sourceforge.net/viewvc/phpmyadmin/branches/QA_2_11/phpMyAdmin/libraries/File.class.php?r1=11528&r2=11527&pathrev=11528
- http://phpmyadmin.svn.sourceforge.net/viewvc/phpmyadmin?view=rev&revision=11528
- http://www.debian.org/security/2010/dsa-2034
- http://www.phpmyadmin.net/home_page/security/PMASA-2010-2.php
