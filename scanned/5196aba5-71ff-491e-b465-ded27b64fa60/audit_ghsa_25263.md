# [M] phpMyAdmin Local file inclusion through transformation feature

## Summary
Severity: Medium
Advisory: GHSA-xc97-r49q-cxgc
CVE: CVE-2018-19968
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-xc97-r49q-cxgc
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=0 <4.8.4

## Details
An attacker can exploit phpMyAdmin before 4.8.4 to leak the contents of a local file because of an error in the transformation feature. The attacker must have access to the phpMyAdmin Configuration Storage tables, although these can easily be created in any database to which the attacker has access. An attacker must have valid credentials to log in to phpMyAdmin; this vulnerability does not allow an attacker to circumvent the login system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19968
- https://github.com/phpmyadmin/phpmyadmin/commit/6a1ba61e29002f0305a9322a8af4eaaeb11c0732
- https://github.com/phpmyadmin/composer
- https://lists.debian.org/debian-lts-announce/2019/02/msg00003.html
- https://security.gentoo.org/glsa/201904-16
- https://www.phpmyadmin.net/security/PMASA-2018-6
- http://www.securityfocus.com/bid/106178
