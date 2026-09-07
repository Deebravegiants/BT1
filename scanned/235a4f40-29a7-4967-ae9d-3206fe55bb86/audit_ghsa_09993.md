# [C] Official Clerk JavaScript SDKs: Middleware-based route protection bypass

## Summary
Severity: Critical
Advisory: GHSA-vqx2-fgx2-5wq9
CVE: CVE-2026-41248
CWE: CWE-436, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-vqx2-fgx2-5wq9
Type: github-advisory

## Affected
- npm: `@clerk/nextjs` — affected >=5.0.0 <5.7.6
- npm: `@clerk/nuxt` — affected >=1.1.0 <1.13.28
- npm: `@clerk/astro` — affected >=0.0.1 <1.5.7
- npm: `@clerk/shared` — affected >=2.20.17 <2.22.1
- npm: `@clerk/nextjs` — affected >=6.0.0-snapshot.vb87a27f <6.39.2
- npm: `@clerk/nextjs` — affected >=7.0.0 <7.2.1
- npm: `@clerk/nuxt` — affected >=2.0.0 <2.2.2
- npm: `@clerk/astro` — affected >=2.0.0-snapshot.v20241206174604 <2.17.10
- npm: `@clerk/astro` — affected >=3.0.0 <3.0.15
- npm: `@clerk/shared` — affected >=3.0.0-canary.v20250225091530 <3.47.4
- npm: `@clerk/shared` — affected >=4.0.0 <4.8.1

## Details
## Summary

`createRouteMatcher` in `@clerk/nextjs`, `@clerk/nuxt`, and `@clerk/astro` can be bypassed by certain crafted requests, allowing them to skip middleware gating and reach downstream handlers.

Sessions are not compromised and no existing user can be impersonated - the bypass only affects the middleware-level gating decision.

## Who is affected

All apps using `createRouteMatcher` should upgrade to the patched versions. Patches are drop-in with no API changes. The information below describes the scope of the bypass and helps you understand whether you are potentially affected, but is not a reason to delay the upgrade.

Apps relying only on middleware gating via `createRouteMatcher` are affected, because a crafted request can skip middleware checks and reach downstream handlers (API routes, server components, etc.). This middleware pattern permits the bypass:

```ts
// Next.js example, equivalent patterns exist in Nuxt and Astro
const isProtectedRoute = createRouteMatcher(['/admin(.*)']);

export default clerkMiddleware(async (auth, req) => {
  if (isProtectedRoute(req)) {
    await auth.protect();
  }
});
```

That said, the bypass is limited to the middleware-level route-matching gate. `clerkMiddleware` still authenticates the request and `auth()` reflects the real authentication state of the caller. Auth checks performed inside your route handlers, server components, or server actions continue to work correctly and are not affected. Whether your app is affected in practice depends on whether you have those downstream checks.

External APIs that authenticate each request with a token are also unaffected on those endpoints, since token verification runs independently.

Additionally, this common middleware pattern correctly blocks the bypass at the middleware layer:

```ts
// Next.js example, equivalent patterns exist in Nuxt and Astro
const isPublicRoute = createRouteMatcher(['/docs(.*)']);

export default clerkMiddleware(async (auth, req) => {
  if (!isPublicRoute(req)) {
    await auth.protect();
  }
});
```

`@clerk/shared` is usually not imported directly in application code, but if you import `createPathMatcher` from an affected `@clerk/shared` version, you are also affected. Run `npm why @clerk/shared` (or your package manager's equivalent) to check your installed version.

## Recommended actions

Install the patched version for your framework (pick the one matching your current major):

**`@clerk/nextjs`**
- v7.x: fixed in `7.2.1`
- v6.x: fixed in `6.39.2`
- v5.x: fixed in `5.7.6`

**`@clerk/nuxt`**
- v2.x: fixed in `2.2.2`
- v1.x: fixed in `1.13.28`

**`@clerk/astro`**
- v3.x: fixed in `3.0.15`
- v2.x: fixed in `2.17.10`
- v1.x: fixed in `1.5.7`

**`@clerk/shared`**
- v4.x: fixed in `4.8.1`
- v3.x: fixed in `3.47.4`
- v2.x: fixed in `2.22.1`

## Workaround

If you cannot upgrade immediately, adding server-side auth checks (`auth()`) inside your route handlers, server components, or server actions provides defense-in-depth against this bypass.

## Timeline

This issue was reported on 13 APR 2026, patched on 15 APR 2026, and publicly disclosed on 15 APR 2026.

Thanks to [Christiaan Swiers](https://github.com/YouGina) for the responsible disclosure of this vulnerability.

## References
- https://github.com/clerk/javascript/security/advisories/GHSA-vqx2-fgx2-5wq9
- https://nvd.nist.gov/vuln/detail/CVE-2026-41248
- https://github.com/clerk/javascript
