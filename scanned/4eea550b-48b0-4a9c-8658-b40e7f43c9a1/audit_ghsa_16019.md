# [H] Laravel environment manipulation via query string

## Summary
Severity: High
Advisory: GHSA-gv7v-rgg6-548h
CVE: CVE-2024-52301
CWE: CWE-88
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:N (CVSS_V3)
Published: 2024-11-12
Source: https://github.com/advisories/GHSA-gv7v-rgg6-548h
Type: github-advisory

## Affected
- Packagist: `laravel/framework` — affected >=0 <6.20.45
- Packagist: `laravel/framework` — affected >=7.0.0 <7.30.7
- Packagist: `laravel/framework` — affected >=8.0.0 <8.83.28
- Packagist: `laravel/framework` — affected >=9.0.0 <9.52.17
- Packagist: `laravel/framework` — affected >=10.0.0 <10.48.23
- Packagist: `laravel/framework` — affected >=11.0.0 <11.31.0

## Details
## Description

When the `register_argc_argv php` directive is set to `on` , and users call any URL with a special crafted query string, they are able to change the environment used by the framework when handling the request.

## Resolution

The framework now ignores argv values for environment detection on non-cli SAPIs.

## References
- https://github.com/laravel/framework/security/advisories/GHSA-gv7v-rgg6-548h
- https://nvd.nist.gov/vuln/detail/CVE-2024-52301
- https://github.com/FriendsOfPHP/security-advisories/blob/master/laravel/framework/CVE-2024-52301.yaml
- https://github.com/advisories/GHSA-gv7v-rgg6-548h
- https://github.com/laravel/framework
- https://lists.debian.org/debian-lts-announce/2024/12/msg00019.html
