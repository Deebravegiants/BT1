# [M] phpMyAdmin ReCaptcha bypass

## Summary
Severity: Medium
Advisory: GHSA-v6fh-vg22-r6cm
CVE: CVE-2015-6830
CWE: CWE-200
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-v6fh-vg22-r6cm
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.3.0 <4.3.13.2
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4.0 <4.4.14.1

## Details
libraries/plugins/auth/AuthenticationCookie.class.php in phpMyAdmin 4.3.x before 4.3.13.2 and 4.4.x before 4.4.14.1 allows remote attackers to bypass a multiple-reCaptcha protection mechanism against brute-force credential guessing by providing a correct response to a single reCaptcha.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-6830
- https://github.com/phpmyadmin/phpmyadmin/commit/0314e67900f01410bc8c81c58a40dc0515e3c91d
- https://github.com/phpmyadmin/phpmyadmin/commit/785f4e2711848eb8945894199d5870253a88584e
- https://web.archive.org/web/20200228052837/http://www.securityfocus.com/bid/76674
- https://web.archive.org/web/20211215060142/http://www.securitytracker.com/id/1033546
- https://www.phpmyadmin.net/security/PMASA-2015-4
- http://lists.fedoraproject.org/pipermail/package-announce/2015-September/166294.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-September/166307.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-September/166531.html
- http://www.debian.org/security/2015/dsa-3382
