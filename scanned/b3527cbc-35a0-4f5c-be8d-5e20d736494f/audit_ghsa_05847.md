# [M] @hono/oauth-providers: OAuth state check fails open on omitted state, enabling login CSRF and forced account linking

## Summary
Severity: Medium
Advisory: GHSA-fm3f-ch8h-qw8q
CVE: CVE-2026-81888
CWE: CWE-352, CWE-1275
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-31
Source: https://github.com/advisories/GHSA-fm3f-ch8h-qw8q
Type: github-advisory

## Affected
- npm: `@hono/oauth-providers` — affected >=0 <0.8.6

## Details
### Summary

The built-in social login providers accept an OAuth callback even when the `state` value is absent on both sides, so the anti-CSRF check passes for a callback that never came from a genuine login attempt. This defeats the `state`-based CSRF protection under default usage.

### Details

The `state` check treated two absent values as a match, so a callback that omits `state` — and for which no `state` was ever stored — was allowed to redeem the authorization code. Hono's `csrf()` middleware does not help: it only inspects form-style requests, while the OAuth callback is a top-level `GET` navigation it treats as safe.

This affects the `google`, `github`, `facebook`, `discord`, `twitch`, `linkedin`, and `msentra` providers. The `x` (Twitter) provider is not exploitable due to its PKCE binding.

### Impact

An attacker can make a victim's browser complete an OAuth callback that binds the attacker's identity instead of the victim's, leading to login CSRF (the victim silently acts inside the attacker's account) or forced account linking (the attacker's identity is linked to the victim's account, enabling later sign-in as the victim). Affects applications using an affected provider on `@hono/oauth-providers` `0.8.5` or earlier.

## References
- https://github.com/honojs/middleware/security/advisories/GHSA-fm3f-ch8h-qw8q
- https://github.com/honojs/middleware/pull/2040
- https://github.com/honojs/middleware/commit/b37765f40b7bddb1d8fce39573b085222dea58c1
- https://github.com/honojs/middleware
- https://github.com/honojs/middleware/releases/tag/%40hono%2Foauth-providers%400.8.6
