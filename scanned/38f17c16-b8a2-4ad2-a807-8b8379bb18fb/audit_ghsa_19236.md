# [C] Auth0 Symfony SDK Vulnerable to Brute Force Authentication Tags of CookieStore Sessions

## Summary
Severity: Critical
Advisory: GHSA-9wg9-93h9-j8ch
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-05-17
Source: https://github.com/advisories/GHSA-9wg9-93h9-j8ch
Type: github-advisory

## Affected
- Packagist: `auth0/symfony` — affected >=0 <5.4.0

## Details
**Overview**
Session cookies of applications using the Auth0 symfony SDK configured with CookieStore have authentication tags that can be brute forced, which may result in unauthorized access.

**Am I Affected?**
You are affected by this vulnerability if you meet the following pre-conditions:
1. Applications using the Auth0 symfony SDK with version <=5.3.1
2. Auth0/Symfony SDK uses the Auth0-PHP SDK with version 8.0.0-BETA1 or higher and below 8.14.0. 
3. Session storage configured with CookieStore.


**Fix**
Upgrade Auth0/symfony to v5.4.0. As an additional precautionary measure, we recommend rotating your cookie encryption keys. Note that once updated, any previous session cookies will be rejected.

**Acknowledgement**
Okta would like to thank Félix Charette for discovering this vulnerability.

## References
- https://github.com/auth0/symfony/security/advisories/GHSA-9wg9-93h9-j8ch
- https://nvd.nist.gov/vuln/detail/CVE-2025-47275
- https://github.com/auth0/symfony/commit/9a7294f08a32f17a0e77c8522a648195b6940340
- https://github.com/auth0/symfony
- https://github.com/auth0/symfony/releases/tag/5.4.0
