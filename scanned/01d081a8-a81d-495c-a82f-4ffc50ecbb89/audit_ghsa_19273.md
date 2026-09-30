# [C] Auth0 Wordpress plugin Vulnerable to Brute Force Authentication Tags of CookieStore Sessions

## Summary
Severity: Critical
Advisory: GHSA-2f4r-34m4-3w8q
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-05-17
Source: https://github.com/advisories/GHSA-2f4r-34m4-3w8q
Type: github-advisory

## Affected
- Packagist: `auth0/wordpress` — affected >=0 <5.3.0

## Details
**Overview**
Session cookies of applications using the Auth0 Wordpress plugin configured with CookieStore have authentication tags that can be brute forced, which may result in unauthorized access.

**Am I Affected?**
You are affected by this vulnerability if you meet the following pre-conditions:
1. Applications using the Auth0 WordPress Plugin with version <=5.2.1
2. Auth0 WordPress Plugin uses the Auth0-PHP SDK with version 8.0.0-BETA1 or higher and below 8.14.0. 
3. Session storage configured with CookieStore.


**Fix**
Upgrade Auth0/wordpress plugin to v5.3.0. As an additional precautionary measure, we recommend rotating your cookie encryption keys. Note that once updated, any previous session cookies will be rejected.

**Acknowledgement**
Okta would like to thank Félix Charette for discovering this vulnerability.

## References
- https://github.com/auth0/wordpress/security/advisories/GHSA-2f4r-34m4-3w8q
- https://nvd.nist.gov/vuln/detail/CVE-2025-47275
- https://github.com/auth0/wordpress/commit/06b64468089472d8b62c881708be7eb3749b35ac
- https://github.com/auth0/wordpress
- https://github.com/auth0/wordpress/releases/tag/5.3.0
