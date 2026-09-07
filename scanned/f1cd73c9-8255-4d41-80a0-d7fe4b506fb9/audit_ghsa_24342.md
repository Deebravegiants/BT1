# [M] phpMyAdmin micro history Implementation XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6wfj-2mw7-p5cg
CVE: CVE-2014-6300
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-6wfj-2mw7-p5cg
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0.0 <4.0.10.3
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.1.0 <4.1.14.4
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.2.0 <4.2.8.1

## Details
Cross-site scripting (XSS) vulnerability in the micro history implementation in phpMyAdmin 4.0.x before 4.0.10.3, 4.1.x before 4.1.14.4, and 4.2.x before 4.2.8.1 allows remote attackers to inject arbitrary web script or HTML, and consequently conduct a cross-site request forgery (CSRF) attack to create a root account, via a crafted URL, related to js/ajax.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-6300
- https://github.com/phpmyadmin/phpmyadmin/commit/33b39f9f1dd9a4d27856530e5ac004e23b30e8ac
- https://security.gentoo.org/glsa/201505-03
- https://web.archive.org/web/20200228081340/http://www.securityfocus.com/bid/69790
- http://lists.opensuse.org/opensuse-updates/2014-09/msg00032.html
- http://www.phpmyadmin.net/home_page/security/PMASA-2014-10.php
