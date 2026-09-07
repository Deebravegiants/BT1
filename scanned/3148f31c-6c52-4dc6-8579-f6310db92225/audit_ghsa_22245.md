# [M] phpBB Cross-Site Request Forgery (CSRF)

## Summary
Severity: Medium
Advisory: GHSA-6mh2-98gr-wv76
CVE: CVE-2019-13376
CWE: CWE-352, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6mh2-98gr-wv76
Type: github-advisory

## Affected
- Packagist: `phpbb/phpbb` — affected >=0 <3.2.8

## Details
phpBB version 3.2.7 allows the stealing of an Administration Control Panel session id by leveraging CSRF in the Remote Avatar feature. The CSRF Token Hijacking leads to stored XSS

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13376
- https://blog.phpbb.com/category/security
- https://github.com/phpbb/phpbb-app
- https://ssd-disclosure.com/archives/4007/ssd-advisory-phpbb-csrf-token-hijacking-leading-to-stored-xss
