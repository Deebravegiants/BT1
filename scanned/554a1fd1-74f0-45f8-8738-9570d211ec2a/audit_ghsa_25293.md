# [M] phpMyAdmin Unsafe Fetching of Javascript Code

## Summary
Severity: Medium
Advisory: GHSA-xpxp-v33m-5jp9
CVE: CVE-2012-5368
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-xpxp-v33m-5jp9
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=3.5 <3.5.3

## Details
phpMyAdmin 3.5.x before 3.5.3 uses JavaScript code that is obtained through an HTTP session to phpmyadmin.net without SSL, which allows man-in-the-middle attackers to conduct cross-site scripting (XSS) attacks by modifying this code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5368
- https://github.com/phpmyadmin/phpmyadmin/commit/50edafc0884aa15d0a1aa178089ac6a1ad2eb18a
- https://github.com/phpmyadmin/phpmyadmin/commit/a547f3d3e2cf36c6a904fa3e053fd8bddd3fbbb0
- https://web.archive.org/web/20200228143700/http://www.securityfocus.com/bid/55939
- http://lists.opensuse.org/opensuse-updates/2012-11/msg00033.html
- http://www.phpmyadmin.net/home_page/security/PMASA-2012-7.php
