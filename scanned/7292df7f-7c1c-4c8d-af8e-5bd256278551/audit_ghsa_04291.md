# [M] Snipe-IT Vulnerable to Privilege Escalation via Missing admin Permission Check in User Creation

## Summary
Severity: Medium
Advisory: GHSA-hf68-g98v-wp9g
CVE: CVE-2026-55483
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-hf68-g98v-wp9g
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.0

## Details
### Impact
The `store()` method in both the web and API `UsersController` only strips the superuser permission when a non-superuser creates a user. It does not strip the admin permission. This allows any authenticated user with the `users.create` permission to create a new user with full admin privileges.

The `users.create permission`  may commonly be delegated to HR staff, department leads, or similar roles.

### Patches
Patched in [aea3877718](https://github.com/grokability/snipe-it/commit/aea3877718158cc2a10c2dde4597b1f439f5f6cb)

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-hf68-g98v-wp9g
- https://github.com/grokability/snipe-it/commit/aea3877718158cc2a10c2dde4597b1f439f5f6cb
- https://github.com/grokability/snipe-it
