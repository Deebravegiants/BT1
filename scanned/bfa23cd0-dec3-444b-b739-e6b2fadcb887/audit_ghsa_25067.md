# [M] Laravel does not properly constrain the host portion of a password-reset URL

## Summary
Severity: Medium
Advisory: GHSA-rc8x-jrrc-frfv
CVE: CVE-2017-9303
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-rc8x-jrrc-frfv
Type: github-advisory

## Affected
- Packagist: `laravel/laravel` — affected >=5.4.0 <5.4.22
- Packagist: `illuminate/auth` — affected >=5.3.0
- Packagist: `illuminate/auth` — affected >=5.4.0 <5.4.22
- Packagist: `laravel/framework` — affected >=5.3.0
- Packagist: `laravel/framework` — affected >=5.4.0 <5.4.22

## Details
Laravel 5.4.x before 5.4.22 does not properly constrain the host portion of a password-reset URL, which makes it easier for remote attackers to conduct phishing attacks by specifying an attacker-controlled host.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9303
- https://github.com/laravel/framework/commit/cef10551820530632a86fa6f1306fee95c5cac43
- https://github.com/FriendsOfPHP/security-advisories/blob/master/illuminate/auth/CVE-2017-9303.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/laravel/framework/CVE-2017-9303.yaml
- https://laravel-news.com/laravel-5-4-22-is-now-released-and-includes-a-security-fix
- https://laravel.com/docs/5.4/releases#laravel-5.4.22
- https://web.archive.org/web/20171021180417/http://www.securityfocus.com/bid/98776
- http://www.securityfocus.com/bid/98776
