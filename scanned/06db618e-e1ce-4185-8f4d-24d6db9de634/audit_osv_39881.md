# [H] OpenReception's logout page clears local access_token before server-side revocation, leaving duplicated tokens valid until expiry

## Summary
Severity: High
Advisory: CVE-2026-48079
Aliases: GHSA-hrhm-m2hm-7cjh
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-48079
Type: osv

## Details
OpenReception's appointment booking software provides an end-to-end encrypted appointment booking platform. Prior to version 1.0.2, when a user navigates to the `/logout` page, the page's server-side load handler deletes the `access_token` cookie before calling `/api/auth/logout` via an internal `event.fetch()`. The internal fetch consequently runs without the auth cookie, so `apiAuthHandle` rejects it, the logout handler never executes, and `SessionService.revokeSession()` is never called for the current session. The DB session row remains valid until its natural expiry (one week by default). The user sees a successful logout (cookie gone, UI returns to login), but any party still holding a copy of the now-deleted access token can continue making authenticated API calls until the session naturally expires. The root cause is a simple ordering mistake. The same auth subsystem implements the correct order in `/api/auth/logout`: revoke the current DB session first, then delete the cookie. The page-level wrapper does the opposite. Version 1.0.2 initiates server-side logout before removing authentication cookies and first appears in version 1.0.2. Version 2.0.0 later replaces this with a race-free client-side logout flow.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48079.json
- https://github.com/open-reception/appointment-booking-software/security/advisories/GHSA-hrhm-m2hm-7cjh
- https://nvd.nist.gov/vuln/detail/CVE-2026-48079
- https://github.com/open-reception/appointment-booking-software/commit/2419f9e87a8abad72f31b1fedeb80c758b30322e
- https://github.com/open-reception/appointment-booking-software/commit/f833dbf50059ff7d4ea42ce7bbb3a5cdcf7a6929
