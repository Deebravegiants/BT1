# [M] Nuxt's route middleware is not enforced when rendering `.server.vue` pages via `/__nuxt_island/page_*`

## Summary
Severity: Medium
Advisory: GHSA-hg3f-28rg-4jxj
CVE: CVE-2026-47200
CWE: CWE-284, CWE-288
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-hg3f-28rg-4jxj
Type: github-advisory

## Affected
- npm: `nuxt` — affected >=3.11.0 <3.21.6
- npm: `@nuxt/nitro-server` — affected >=3.20.0 <3.21.6
- npm: `@nuxt/nitro-server` — affected >=4.2.0 <4.4.6
- npm: `nuxt` — affected >=4.0.0-alpha.1 <4.4.6

## Details
### Summary

When `experimental.componentIslands` is enabled (default in Nuxt 4), any `.server.vue` file under `pages/` is automatically registered as a server island under the key `page_<routeName>` and exposed via the `/__nuxt_island/:name` endpoint. Until this fix, requests through that endpoint rendered the page component directly via the SSR renderer without instantiating Vue Router, which meant route middleware declared on the page (including `definePageMeta({ middleware })`) did not run.

For Nuxt applications that gate a `.server.vue` *page* behind route middleware as their sole auth check, an unauthenticated attacker could bypass that check by requesting `/__nuxt_island/page_<routeName>_<anyhash>` directly and receiving the server-rendered HTML.

### Affected configurations

All three conditions must hold for an application to be vulnerable:

1. `experimental.componentIslands` is enabled (the default in Nuxt 4; opt-in in Nuxt 3).
2. The application defines one or more `.server.vue` files under `pages/`, registering them as routed pages.
3. Authentication / authorization for at least one such page is enforced solely via route middleware (`middleware/*.ts` referenced from `definePageMeta`), without a server-side check inside the page or its data layer.

Applications that enforce auth inside the island's own data layer (server-only API routes, `useRequestEvent` + manual session checks, etc.) were not affected. The general "route middleware does not run for non-page island *components*" behaviour is documented and unchanged; this advisory concerns the `.server.vue` *page* case specifically, where running middleware is the user's clear expectation.

### Details

- Build (`packages/nuxt/src/components/templates.ts`): `.server.vue` pages are registered as island components with `page_` prefix, making them addressable through `/__nuxt_island/page_<routeName>_<hashId>`.
- Runtime (`packages/nitro-server/src/runtime/handlers/island.ts`): the handler resolves the requested island component and renders it via `renderer.renderToString(ssrContext)`. The Vue Router plugin previously short-circuited middleware execution whenever `ssrContext.islandContext` was set.
- The two paths interact so that route middleware declared on the source page never runs.

### Proof of concept

Given a page `app/pages/secret.server.vue`:

```vue
<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
</script>

<template>
<h1>SECRET DATA</h1>
</template>
```

with `middleware/auth.ts` blocking unauthenticated access:

```bash
# Direct page request: blocked by middleware
curl -i http://localhost:3000/secret
# -> 403 / redirect, depending on the middleware

# Island request: middleware did not run before this fix
curl -i 'http://localhost:3000/__nuxt_island/page_secret_anyhash'
# -> 200 OK, body includes <h1>SECRET DATA</h1>
```

### Patches

Patched in `nuxt@4.4.6` and `nuxt@3.21.6` by [#35092](https://github.com/nuxt/nuxt/pull/35092). The Vue Router plugin now runs middleware and redirect handling for `page_*` islands (i.e. islands that originate from `.server.vue` files in `pages/`). The island handler propagates middleware-issued responses (`~renderResponse`), and a new `beforeResolve` guard returns HTTP 400 when the requested `page_<name>` does not match the route component the URL resolves to.

Non-page island components are unaffected - they continue to render without route middleware, by design.

### Workarounds

If you cannot upgrade immediately:

- Enforce authentication inside the `.server.vue` page itself, not via route middleware. Read the session from `useRequestEvent()` and `throw createError({ statusCode: 401 })` (or redirect) before returning data. This is the recommended pattern for islands regardless of this advisory.
- Disable `experimental.componentIslands` if your app does not use the feature.
- If your app must keep route-middleware-only auth, gate the `/__nuxt_island/page_*` URL prefix at your reverse proxy or in a server middleware.

## References
- https://github.com/nuxt/nuxt/security/advisories/GHSA-hg3f-28rg-4jxj
- https://nvd.nist.gov/vuln/detail/CVE-2026-47200
- https://github.com/nuxt/nuxt/issues/19772
- https://github.com/nuxt/nuxt/pull/35092
- https://github.com/nuxt/nuxt
