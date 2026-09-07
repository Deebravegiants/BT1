# [H] phpMyAdmin Unsafe comparison of XSRF/CSRF token

## Summary
Severity: High
Advisory: GHSA-8m97-xc46-rw9w
CVE: CVE-2016-2041
CWE: CWE-203
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-8m97-xc46-rw9w
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0 <4.0.10.13
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4 <4.4.15.3
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.5 <4.5.4

## Details
libraries/common.inc.php in phpMyAdmin 4.0.x before 4.0.10.13, 4.4.x before 4.4.15.3, and 4.5.x before 4.5.4 does not use a constant-time algorithm for comparing CSRF tokens, which makes it easier for remote attackers to bypass intended access restrictions by measuring time differences.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2041
- https://github.com/phpmyadmin/phpmyadmin/commit/ec0e88e37ef30a66eada1c072953f4ec385a3e49
- https://github.com/phpmyadmin/composer
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176483.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176739.html
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00028.html
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00049.html
- http://www.debian.org/security/2016/dsa-3627
- http://www.phpmyadmin.net/home_page/security/PMASA-2016-5.php
