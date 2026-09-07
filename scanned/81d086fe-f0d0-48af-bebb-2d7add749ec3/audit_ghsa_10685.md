# [C] Better Auth Has Two-Factor Authentication Bypass via Premature Session Caching (session.cookieCache)

## Summary
Severity: Critical
Advisory: GHSA-xg6x-h9c9-2m83
CWE: CWE-288
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-xg6x-h9c9-2m83
Type: github-advisory

## Affected
- npm: `better-auth` — affected >=0 <1.4.9

## Details
### Summary

Under certain configurations, sessions may be considered valid before two-factor authentication (2FA) is fully completed. This can allow access to authenticated routes without verifying the second factor.

---

### Description

When two-factor authentication is enabled, the authentication flow correctly identifies users who require additional verification and defers full authentication until the second factor is completed.

However, when `session.cookieCache` is enabled, the session generated during the initial sign-in step may be cached as valid **prior to 2FA verification**. Subsequent session lookups may then return this cached session without re-evaluating the 2FA requirement.

This results in a situation where session validity can be established before all authentication constraints are satisfied.

---

### Impact

An attacker (or user) with valid primary credentials may gain access to protected application routes without completing the required second authentication factor.

Any application using `better-auth` with both two-factor authentication and session cookie caching enabled may be affected.

---

### Mitigation

* Upgrade to a version of `better-auth` that includes the fix for this issue.
* Ensure that session caching does not treat sessions as fully authenticated until all required authentication steps, including 2FA, are completed.
* As a temporary workaround, disable `session.cookieCache` when using two-factor authentication.

## References
- https://github.com/better-auth/better-auth/security/advisories/GHSA-xg6x-h9c9-2m83
- https://github.com/better-auth/better-auth
