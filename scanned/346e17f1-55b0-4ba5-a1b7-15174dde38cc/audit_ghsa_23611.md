# [M] phpMyAdmin Cryptographic Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9xhq-pm7v-693p
CVE: CVE-2016-9847
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9xhq-pm7v-693p
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6 <4.6.5
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4 <4.4.15.9
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0 <4.0.10.18

## Details
An issue was discovered in phpMyAdmin. When the user does not specify a blowfish_secret key for encrypting cookies, phpMyAdmin generates one at runtime. A vulnerability was reported where the way this value is created uses a weak algorithm. This could allow an attacker to determine the user's blowfish_secret and potentially decrypt their cookies. All 4.6.x versions (prior to 4.6.5), 4.4.x versions (prior to 4.4.15.9), and 4.0.x versions (prior to 4.0.10.18) are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9847
- https://security.gentoo.org/glsa/201701-32
- https://web.archive.org/web/20210123194700/http://www.securityfocus.com/bid/94524
- https://www.phpmyadmin.net/security/PMASA-2016-58
