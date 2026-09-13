# [M] Auth0-PHP SDK has Improper Audience Validation

## Summary
Severity: Medium
Advisory: GHSA-j2vm-wrq3-f7gf
CVE: CVE-2025-68129
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-12-17
Source: https://github.com/advisories/GHSA-j2vm-wrq3-f7gf
Type: github-advisory

## Affected
- Packagist: `auth0/auth0-php` — affected >=8.0.0 <8.18.0

## Details
### Description
In applications built with the Auth0-PHP SDK, the audience validation in access tokens is performed improperly. Without proper validation, affected applications may accept ID tokens as Access tokens.
### Affected product and versions
Projects are affected if they meet the following preconditions:

- Applications using the Auth0-PHP SDK, versions between v8.0.0 and v8.17.0, or
- Applications using the following SDKs that rely on the Auth0-PHP SDK versions between v8.0.0 and v8.17.0:
    - a. Auth0/symfony,
    - b. Auth0/laravel-auth0,
    - c. Auth0/wordpress.

### Resolution
Upgrade Auth0/Auth0-PHP to version 8.18.0 or greater.

### Acknowledgement
Okta would like to thank Jafar Sadiq (iaf4r) for their discovery and responsible disclosure.

## References
- https://github.com/auth0/auth0-PHP/security/advisories/GHSA-j2vm-wrq3-f7gf
- https://github.com/auth0/laravel-auth0/security/advisories/GHSA-7hh9-gp72-wh7h
- https://github.com/auth0/symfony/security/advisories/GHSA-f3r2-88mq-9v4g
- https://github.com/auth0/wordpress/security/advisories/GHSA-vvg7-8rmq-92g7
- https://nvd.nist.gov/vuln/detail/CVE-2025-68129
- https://github.com/auth0/auth0-PHP/commit/7fe700053aee609718460c123f00f53c511f0f7f
- https://github.com/auth0/laravel-auth0/commit/a1c3344dc0e5a36e8f56c8cfc535728d3d7558f3
- https://github.com/auth0/symfony/commit/0103d6f8dcef6996653fad1f823d1c167f472479
- https://github.com/auth0/wordpress/commit/b207c6f7fd06507b90c4e6bcc18a857ef9e018de
- https://github.com/auth0/auth0-PHP
- https://github.com/auth0/auth0-PHP/releases/tag/8.18.0
- https://github.com/auth0/laravel-auth0/releases/tag/7.20.0
- https://github.com/auth0/symfony/releases/tag/5.6.0
- https://github.com/auth0/wordpress/releases/tag/5.5.0
