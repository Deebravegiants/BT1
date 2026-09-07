# [M] Craft CMS Race condition in Token Service potentially allows for token usage greater than the token limit

## Summary
Severity: Medium
Advisory: GHSA-6fx5-5cw5-4897
CVE: CVE-2026-27128
CWE: CWE-367
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-02-23
Source: https://github.com/advisories/GHSA-6fx5-5cw5-4897
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.5.0-RC1 <4.16.19
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.8.23

## Details
A Time-of-Check-Time-of-Use (TOCTOU) race condition exists in Craft CMS’s token validation service for tokens that explicitly set a limited usage. The `getTokenRoute()` method reads a token’s usage count, checks if it’s within limits, then updates the database in separate non-atomic operations. By sending concurrent requests, an attacker can use a single-use impersonation token multiple times before the database update completes.

To make this work, an attacker needs to obtain a valid user account impersonation URL with a non-expired token via some other means and exploit a race condition while bypassing any rate-limiting rules in place.

For this to be a privilege escalation, the impersonation URL must include a token for a user account with more permissions than the current user.

## References

https://github.com/craftcms/cms/commit/3e4afe18279951c024c64896aa2b93cda6d95fdf

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-6fx5-5cw5-4897
- https://nvd.nist.gov/vuln/detail/CVE-2026-27128
- https://github.com/craftcms/cms/commit/3e4afe18279951c024c64896aa2b93cda6d95fdf
- https://github.com/craftcms/cms
