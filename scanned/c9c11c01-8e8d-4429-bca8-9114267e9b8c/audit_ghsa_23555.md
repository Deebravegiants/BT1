# [M] phpMyAdmin vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-6q2j-8h8q-46mr
CVE: CVE-2016-5705
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-6q2j-8h8q-46mr
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4.0 <4.4.15.7
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6.0 <4.6.3

## Details
Multiple cross-site scripting (XSS) vulnerabilities in phpMyAdmin 4.4.x before 4.4.15.7 and 4.6.x before 4.6.3 allow remote attackers to inject arbitrary web script or HTML via vectors involving (1) server-privileges certificate data fields on the user privileges page, (2) an "invalid JSON" error message in the error console, (3) a database name in the central columns implementation, (4) a group name, or (5) a search name in the bookmarks implementation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5705
- https://github.com/phpmyadmin/phpmyadmin/commit/03f73d48369703e0d3584699b08e24891c3295b8
- https://github.com/phpmyadmin/phpmyadmin/commit/0b7416c5f4439ed3f11c023785f2d4c49a1b09fc
- https://github.com/phpmyadmin/phpmyadmin/commit/364732e309cccb3fb56c938ed8d8bc0e04a3ca98
- https://github.com/phpmyadmin/phpmyadmin/commit/36df83a97a7f140fdb008b727a94f882847c6a6f
- https://github.com/phpmyadmin/phpmyadmin/commit/57ae483bad33059a885366d5445b7e1f6f29860a
- https://github.com/phpmyadmin/phpmyadmin
- https://security.gentoo.org/glsa/201701-32
- https://web.archive.org/web/20200227223416/http://www.securityfocus.com/bid/91378
- https://www.phpmyadmin.net/security/PMASA-2016-21
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00113.html
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00114.html
- http://www.debian.org/security/2016/dsa-3627
