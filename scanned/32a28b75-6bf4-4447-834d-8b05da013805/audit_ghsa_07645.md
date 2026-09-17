# [M] Directus Vulnerable to User Enumeration via Password Reset Timing Attack

## Summary
Severity: Medium
Advisory: GHSA-jr94-gj3h-c8rf
CVE: CVE-2026-26185
CWE: CWE-203
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-12
Source: https://github.com/advisories/GHSA-jr94-gj3h-c8rf
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <11.14.1
- npm: `@directus/api` — affected >=0 <32.2.0

## Details
### Summary

A timing-based user enumeration vulnerability exists in the password reset functionality. When an invalid reset_url parameter is provided, the response time differs by approximately 500ms between existing and non-existing users, enabling reliable user enumeration.

### Details

The password reset endpoint implements a timing protection mechanism to prevent user enumeration; however, URL validation executes before the timing protection is applied. This allows an attacker to distinguish between valid and invalid user accounts based on response timing differences.

### Impact

This vulnerability violates user privacy and may facilitate targeted phishing attacks by allowing attackers to confirm the existence of user accounts.

## References
- https://github.com/directus/directus/security/advisories/GHSA-jr94-gj3h-c8rf
- https://nvd.nist.gov/vuln/detail/CVE-2026-26185
- https://github.com/directus/directus/pull/26485
- https://github.com/directus/directus/commit/e69aa7a5248c6e3e822cb1ac354dee295df90b2a
- https://github.com/directus/directus
- https://github.com/directus/directus/releases/tag/v11.14.1
