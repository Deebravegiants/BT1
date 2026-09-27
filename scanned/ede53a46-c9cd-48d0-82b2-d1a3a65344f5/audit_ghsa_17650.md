# [C] Auth0 Wordpress Plugin vulnerable to Deserialization of Untrusted Data

## Summary
Severity: Critical
Advisory: GHSA-862m-5253-832r
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-06-05
Source: https://github.com/advisories/GHSA-862m-5253-832r
Type: github-advisory

## Affected
- Packagist: `auth0/wordpress` — affected >=5.0.0-BETA0 <5.1.0

## Details
**Overview**
The Auth0 Wordpress plugin contains a critical vulnerability due to insecure deserialization of cookie data. If exploited, since SDKs process cookie content without prior authentication, a threat actor could send a specially crafted cookie containing malicious serialized data.

**Am I Affected?**
You are affected by this vulnerability if you meet the following preconditions:

1. Applications using the Auth0 WordPress plugin, versions between 5.0.0 BETA-0 to 5.0.1. 
2. Auth0 WordPress plugin uses the Auth0-PHP SDK with version 8.0.0-BETA3 to 8.3.0.

**Fix**
Upgrade the Auth0 WordPress plugin to the latest version (v5.3.0).

## References
- https://github.com/auth0/auth0-PHP/security/advisories/GHSA-v9m8-9xxp-q492
- https://github.com/auth0/laravel-auth0/security/advisories/GHSA-c42h-56wx-h85q
- https://github.com/auth0/symfony/security/advisories/GHSA-98j6-67v3-mw34
- https://github.com/auth0/wordpress/security/advisories/GHSA-862m-5253-832r
- https://nvd.nist.gov/vuln/detail/CVE-2025-48951
- https://github.com/auth0/wordpress
