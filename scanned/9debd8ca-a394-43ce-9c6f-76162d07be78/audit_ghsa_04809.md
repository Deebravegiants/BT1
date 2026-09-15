# [H] Nuxt: Route-rule middleware bypass via case-sensitivity mismatch between vue-router and the routeRules matcher

## Summary
Severity: High
Advisory: GHSA-mm7m-92g8-7m47
CVE: CVE-2026-53721
CWE: CWE-178, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-mm7m-92g8-7m47
Type: github-advisory

## Affected
- npm: `nuxt` — affected >=4.0.0 <4.4.7
- npm: `nuxt` — affected >=3.11.0 <3.21.7

## Details
## Impact

Nuxt looks up `routeRules` for the current navigation by calling
`getRouteRules({ path: to.path })` from the page-router plugin and the
no-pages router plugin. The compiled `routeRules` matcher (built on
`rou3`) performs case-sensitive matching, while vue-router is configured
with its default `sensitive: false` and matches paths case-insensitively.

The two routers therefore disagree on which rules apply to a given
request path: vue-router still matches the page record for
`/Admin/dashboard`, but the `routeRules` lookup for the same path
returns no match. Any `appMiddleware` declared via `routeRules` is never
added to the middleware set and never runs, on both SSR and client
navigations. The same path skips other path-keyed route rules in the
same way (`ssr`, `redirect`, `appLayout`, and the prerender / payload
hints used client-side).

For applications using `routeRules` with `appMiddleware` as an
authorization gate (a documented pattern), an attacker can flip the case
of any static segment in a protected URL (for example `/Admin/dashboard`
instead of `/admin/dashboard`) to render the protected page with the
middleware skipped. The server returns the fully server-rendered page
including any `useFetch` / `useAsyncData` results captured during SSR.

This is an instance of CWE-178 (Improper Handling of Case Sensitivity)
leading to CWE-863 (Incorrect Authorization) for apps that treat
`appMiddleware` as an authorization boundary.

## Mitigating factors

- Only affects apps that use `routeRules.appMiddleware`. The more
  idiomatic `definePageMeta({ middleware })` is bound to the matched
  route record and is unaffected.
- Nuxt route middleware is documented as an app-layer concern, not a
  server-side auth boundary; well-built apps enforce authorization
  again at the API / data-fetching layer.
- Apps that explicitly set `router.options.sensitive = true` are not
  affected.

## Patches

Fixed in `nuxt@4.4.7` (commit [`07e39cd6`](https://github.com/nuxt/nuxt/commit/07e39cd6f26e407b4192b7865bd17bc44536b9bb)) and backported to `nuxt@3.21.7` (commit [`3f3e3fa7`](https://github.com/nuxt/nuxt/commit/3f3e3fa7b5eec8e495f4f8ce0a54813a8875a11e)). The fix normalizes the path used for `routeRules` lookups so it matches vue-router's default case-insensitive semantics.

## Workarounds

Until you can upgrade, you can mitigate by either:

1. Setting `router.options.sensitive = true` so vue-router matches
   case-sensitively (this changes route-matching behaviour app-wide).
2. Moving security-critical middleware off `routeRules.appMiddleware`
   and onto `definePageMeta({ middleware: [...] })` on the protected
   page components, which is bound to the matched record.
3. Enforcing authorization at the API / data-fetching layer (which you
   should be doing in any case).

## Credit

Reported by Anthropic / Claude through Anthropic's coordinated
vulnerability disclosure process. Reference: ANT-2026-9FSEBYMC.

## References
- https://github.com/nuxt/nuxt/security/advisories/GHSA-mm7m-92g8-7m47
- https://nvd.nist.gov/vuln/detail/CVE-2026-53721
- https://github.com/nuxt/nuxt/commit/07e39cd6f26e407b4192b7865bd17bc44536b9bb
- https://github.com/nuxt/nuxt/commit/3f3e3fa7b5eec8e495f4f8ce0a54813a8875a11e
- https://github.com/nuxt/nuxt
