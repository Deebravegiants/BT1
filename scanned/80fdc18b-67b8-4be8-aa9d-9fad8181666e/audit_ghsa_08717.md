# [M] NocoDB: Refresh Token Cookie Set Without `secure` and `sameSite` Flags

## Summary
Severity: Medium
Advisory: GHSA-f74w-272x-mqcv
CVE: CVE-2026-46550
CWE: CWE-614
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-f74w-272x-mqcv
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0

## Details
### Summary

The refresh-token cookie was set with `httpOnly: true` but missing both the `secure` flag and the `sameSite` attribute. Over plain HTTP the cookie could be intercepted on the network; without `sameSite`, browsers attached it to cross-site POSTs, enabling CSRF against the token-refresh endpoint.

### Details

In `packages/nocodb/src/services/users/helpers.ts`, `setTokenCookie` produced the cookie with only `httpOnly`, an `expires` date, and an optional `domain` from `NC_BASE_HOST_NAME` — no `secure`, no `sameSite`. The refresh endpoint `POST /api/v2/auth/token/refresh` (`auth.controller.ts`) read the cookie unconditionally and returned a new JWT, with no CSRF token.

The fix sets `httpOnly: true`, `sameSite: 'lax'`, and conditional `secure: req.ncSiteUrl.startsWith('https')` so the flag is active under HTTPS while still functional on plain-HTTP localhost development.

This is distinct from GHSA-x4vh-j75g-268g (refresh-token lifecycle on password reset) — different root cause, different attack vector.

### Impact

- Cookie interception on plain HTTP networks (no `secure`).
- Cross-site refresh: malicious cross-origin pages could trigger token refresh and, combined with any same-origin XSS or open-redirect on the NocoDB domain, capture the new JWT.
- Refresh tokens have multi-day expiry (`NC_REFRESH_TOKEN_EXP_IN_DAYS`), so the exposure window is long.

### Credit

This issue was reported by [@ik0z](https://github.com/ik0z).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-f74w-272x-mqcv
- https://nvd.nist.gov/vuln/detail/CVE-2026-46550
- https://github.com/nocodb/nocodb
