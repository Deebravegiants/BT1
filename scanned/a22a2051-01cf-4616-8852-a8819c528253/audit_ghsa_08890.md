# [M] Strapi has a rate limit bypass on users-permissions plugin via attacker-controlled email keying

## Summary
Severity: Medium
Advisory: GHSA-7mqx-wwh4-f9fw
CVE: CVE-2025-64526
CWE: CWE-307
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-7mqx-wwh4-f9fw
Type: github-advisory

## Affected
- npm: `@strapi/plugin-users-permissions` — affected >=0 <5.45.0

## Details
### Summary of CVE-2025-64526 Vulnerability Details

- CVE: CVE-2025-64526
- CVSS v3.1 Vector: `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N` (6.9 — Medium)
- Affected Versions: `@strapi/plugin-users-permissions` <=5.44.0
- How to Patch: Immediately update your Strapi to >=5.45.0

### Description of CVE-2025-64526

In Strapi versions prior to 5.45.0, the rate-limit middleware in the users-permissions plugin derived its rate-limit key in part from `ctx.request.body.email`, including on routes whose body schema does not contain an `email` field (`/auth/local`, `/auth/reset-password`, `/auth/change-password`). An unauthenticated attacker could include an arbitrary `email` value in the request body to obtain a fresh rate-limit key per request, effectively bypassing per-IP throttling on those routes and enabling high-volume credential brute-force, password-reset code brute-force, and credential-stuffing attempts.

The rate-limit key was constructed as `${userIdentifier}:${requestPath}:${ctx.request.ip}`, where `userIdentifier = ctx.request.body.email`. On routes that legitimately use email as their identifier (e.g. `/auth/forgot-password`, `/auth/local/register`), this scoping is correct. On routes that use a different identifier (`identifier` for login, `code` for password reset, `currentPassword` for password change), the email field was not part of the route contract, but the middleware still incorporated it into the key, allowing a caller to rotate the value and obtain a unique key on every request.

The patch maintains an allow-list of routes that legitimately key on the email field and excludes that key component on every other route the middleware is mounted on. OAuth callback paths (`/connect/*`) are treated identifier-less. On routes outside the allow-list, the middleware now falls back to a fixed identifier-less key, ensuring per-IP throttling remains effective even when the request body is attacker-controlled.

### IoC's for CVE-2025-64526

Indicators that an instance running an unpatched version may have been exploited:

- Unusually high volumes of `POST` requests to `/api/auth/local`, `/api/auth/reset-password`, or `/api/auth/change-password` from a single IP within a 5-minute window without 429 (Too Many Requests) responses
- Request bodies on `/api/auth/local` containing both `identifier` AND `email` fields where `email` varies per request. Body shape regex: `"identifier"\s*:\s*"[^"]*",\s*"email"\s*:\s*"[^"]*"`
- Request bodies on `/api/auth/reset-password` containing an unexpected `email` field alongside `code`. Body shape regex: `"code"\s*:\s*"[^"]*",.*"email"\s*:`
- Server logs showing many distinct rate-limit key prefixes for the same IP+route combination within the rate-limit window
- Successful authentication or password reset following hundreds of preceding 401/400 responses from the same IP

## References
- https://github.com/strapi/strapi/security/advisories/GHSA-7mqx-wwh4-f9fw
- https://nvd.nist.gov/vuln/detail/CVE-2025-64526
- https://github.com/strapi/strapi/pull/24818
- https://github.com/strapi/strapi/commit/5e0d243cba9830e6f791de6a94798bcde51468db
- https://github.com/strapi/strapi
- https://github.com/strapi/strapi/releases/tag/v5.45.0
