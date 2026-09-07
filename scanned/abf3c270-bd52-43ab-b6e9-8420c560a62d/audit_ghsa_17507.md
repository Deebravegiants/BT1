# [C] Auth0-PHP SDK Deserialization of Untrusted Data vulnerability

## Summary
Severity: Critical
Advisory: GHSA-v9m8-9xxp-q492
CVE: CVE-2025-48951
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-06-04
Source: https://github.com/advisories/GHSA-v9m8-9xxp-q492
Type: github-advisory

## Affected
- Packagist: `auth0/auth0-php` — affected >=8.0.0-BETA3 <8.3.1

## Details
**Overview**
The Auth0 PHP SDK contains a vulnerability due to insecure deserialization of cookie data. If exploited, since SDKs process cookie content without prior authentication, a threat actor could send a specially crafted cookie containing malicious serialized data.

**Am I Affected?**
You are affected by this vulnerability if you meet the following preconditions:

1. Applications using the Auth0-PHP SDK, versions between 8.0.0-BETA3 to 8.3.0. 
2. Applications using the following SDKs that rely on the Auth0-PHP SDK versions between 8.0.0-BETA3 to 8.3.0:
    a. Auth0/symfony,
    b. Auth0/laravel-auth0,
    c. Auth0/wordpress.

**Fix**
Upgrade Auth0/Auth0-PHP to 8.3.1.

**Acknowledgement**
Okta would like to thank Andreas Forsblom for discovering this vulnerability.

## References
- https://github.com/auth0/auth0-PHP/security/advisories/GHSA-v9m8-9xxp-q492
- https://github.com/auth0/laravel-auth0/security/advisories/GHSA-c42h-56wx-h85q
- https://github.com/auth0/symfony/security/advisories/GHSA-98j6-67v3-mw34
- https://github.com/auth0/wordpress/security/advisories/GHSA-862m-5253-832r
- https://nvd.nist.gov/vuln/detail/CVE-2025-48951
- https://github.com/auth0/auth0-PHP/commit/04b1f5daa8bdfebc5e740ec5ca0fb2df1648a715
- https://github.com/auth0/auth0-PHP
