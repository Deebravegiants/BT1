# [M] Laravel Sensitive Data Exposure

## Summary
Severity: Medium
Advisory: GHSA-c2v7-j5gq-wcq4
CVE: CVE-2017-14775
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-c2v7-j5gq-wcq4
Type: github-advisory

## Affected
- Packagist: `laravel/framework` — affected >=0 <5.5.10
- Packagist: `illuminate/auth` — affected >=0 <5.5.10

## Details
Laravel before 5.5.10 mishandles the remember_me token verification process because DatabaseUserProvider does not have constant-time token comparison.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-14775
- https://github.com/laravel/framework/pull/21320
- https://github.com/FriendsOfPHP/security-advisories/blob/master/illuminate/auth/CVE-2017-14775.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/laravel/framework/CVE-2017-14775.yaml
- https://github.com/laravel/framework/releases/tag/v5.5.10
- https://laravel-news.com/laravel-v5-5-11
