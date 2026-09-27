# [H] Nuxt route rules silently dropped for mixed-case paths, bypassing appMiddleware auth gates (incomplete fix for CVE-2026-53721)

## Summary
Severity: High
Advisory: GHSA-hxvh-4h3w-prp9
CVE: CVE-2026-71315
CWE: CWE-178, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-hxvh-4h3w-prp9
Type: github-advisory

## Affected
- npm: `nuxt` — affected >=4.4.7 <4.5.1
- npm: `nuxt` — affected >=3.21.7 <3.21.10

## Details
### Impact

Nuxt matches route rules case-insensitively by default (mirroring vue-router's default `sensitive: false` routing). The fix for GHSA-mm7m-92g8-7m47 / CVE-2026-53721 lowercased the *lookup* path before matching route rules, but the route-rule *keys* compiled into the matcher were left verbatim. As a result, any route rule whose key contains an uppercase character (for example `/Admin`, `/Dashboard/**`, or the rules Nuxt derives from PascalCase/camelCase page files such as `pages/Admin.vue`) never matches, because every lookup is folded to lowercase while the key stays mixed-case.

vue-router still serves the page case-insensitively, so the page renders with none of its Nuxt route-rule protections applied. The most serious consequence is an authorization bypass: an `appMiddleware` rule used as an auth gate (`routeRules: { '/Admin/dashboard': { appMiddleware: 'auth' } }`) is dropped, and `/Admin/dashboard`, `/admin/dashboard`, and `/ADMIN/dashboard` all render the protected page (and its SSR-fetched data) to an unauthenticated visitor instead of redirecting to login. The same gap drops Nuxt's other app-side route-rule behaviours for mixed-case keys, including the client redirect middleware, the app-side `ssr: false` decision, `prerender`, and payload handling.

### Patches

Fixed in `nuxt@4.5.1` (4.x) and `nuxt@3.21.10` (3.x). The route-rule matcher now case-folds the compiled keys the same way it folds the lookup path, so key and lookup normalisation are symmetric. Both sides are gated on `router.options.sensitive`: with `sensitive: true` (case-sensitive routing) configured casing is preserved on both sides.

Scope note: server-emitted per-route `headers`, server `redirect`, and `proxy` are matched by Nitro's own case-sensitive route-rule matcher, not by Nuxt's app-level matcher. They are unchanged by this advisory. The fix covers the app-level protections Nuxt owns (`appMiddleware`, `appLayout`, the client redirect middleware, the app `ssr` decision, `prerender`, and payload).

### Workarounds

If you cannot upgrade immediately, any one of:

- Key all `routeRules` (and name your page files) in lowercase, so the keys already match the folded lookup path.
- Set `router: { options: { sensitive: true } }` so routing and route-rule matching are both case-sensitive and exact (requests must then use the exact casing).
- Enforce the sensitive protections server-side independently of route rules (for example a server middleware that checks auth), which does not rely on case-insensitive route-rule matching.

## References
- https://github.com/nuxt/nuxt/security/advisories/GHSA-hxvh-4h3w-prp9
- https://github.com/nuxt/nuxt/commit/619963309e082190bac4a26b05f2dd155b039b81
- https://github.com/nuxt/nuxt/commit/ad624a75ad2d215f43633f6b40be346a7194d34d
- https://github.com/nuxt/nuxt
- https://github.com/nuxt/nuxt/releases/tag/v3.21.10
- https://github.com/nuxt/nuxt/releases/tag/v4.5.1
