# [M] phpMyAdmin CSRF Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-mfr9-pcm3-6mwc
CVE: CVE-2019-12616
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mfr9-pcm3-6mwc
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=0 <4.9.0

## Details
An issue was discovered in phpMyAdmin before 4.9.0. A vulnerability was found that allows an attacker to trigger a CSRF attack against a phpMyAdmin user. The attacker can trick the user, for instance through a broken `<img>` tag pointing at the victim's phpMyAdmin database, and the attacker can potentially deliver a payload (such as a specific INSERT or DELETE statement) to the victim.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12616
- https://github.com/phpmyadmin/phpmyadmin/commit/015c404038c44279d95b6430ee5a0dddc97691ec
- https://packetstormsecurity.com/files/153251/phpMyAdmin-4.8-Cross-Site-Request-Forgery.html
- https://www.phpmyadmin.net/security/PMASA-2019-4
