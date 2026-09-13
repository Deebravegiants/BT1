# [M] Astro: Unauthenticated path override in the @astrojs/vercel ISR function

## Summary
Severity: Medium
Advisory: GHSA-x27w-589x-frm2
CVE: CVE-2026-73424
CWE: CWE-441, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-x27w-589x-frm2
Type: github-advisory

## Affected
- npm: `@astrojs/vercel` — affected >=10.0.3 <11.0.3

## Details
## Summary
When ISR is enabled, the serverless entrypoint lets an unauthenticated request
decide which route the origin renders. The internal `_isr` function reads the
`x_astro_path` query parameter and rewrites the request path to it without any
authentication. Edge level access controls only ever see the `/_isr` path, so
they do not apply to the route that actually gets rendered. This is the same
confused deputy problem as CVE-2026-33768, reachable again through the ISR path.

## Impact
This affects apps that use `@astrojs/vercel` with `isr: true` and protect routes
at the edge. Two common setups are affected:

1. Path rules or firewall deny rules configured on Vercel (for example blocking
   `/admin`).
2. Split deployments (`edgeMiddleware: true`) where authorization lives in Astro
   middleware, since that middleware runs at the edge and not in the origin.

An attacker reads any GET rendered route by requesting
`/_isr?x_astro_path=/the/protected/path`. No credentials are required. The
protected content is produced by a fresh origin render, so the attack does not
depend on the response being cached first.

## Details
`packages/integrations/vercel/src/serverless/entrypoint.ts` picks the real path
like this:

```js
if (hasValidMiddlewareSecret) {
  realPath = request.headers.get(ASTRO_PATH_HEADER);       // secret checked
} else if (request.headers.get('x-vercel-isr') === '1') {
  realPath = url.searchParams.get(ASTRO_PATH_PARAM);        // no secret checked
}
```

The header path is gated by the per build secret and is fine. The ISR branch is
not. Two facts make it reachable by anyone:

1. The `_isr` function is publicly addressable.
2. Vercel sets `x-vercel-isr: 1` on requests to it, including direct external
   requests, so the attacker does not even need to send that header.

So `GET /_isr?x_astro_path=/admin` sets the internal path to `/admin` and renders
it. The edge saw only `/_isr`, which is allowed, so any path based rule on
`/admin` never fires. In split deployments the edge middleware also runs against
`/_isr`, and the origin does not run middleware at all, so middleware based auth
is skipped as well.

## How this regressed
CVE-2026-33768 was fixed in 10.0.2 by commit 335a204161 (PR #15959), which
required the secret for every path override and removed the query parameter
source. Commit aa266364fe (PR #16079, "Fix ISR path rewrite to prevent 404")
brought the query parameter back, guarded only by the `x-vercel-isr` header. That
header is not a security boundary, so the fix was effectively undone for ISR
routes starting in 10.0.3.

Worth noting the contrast: the original report treated Edge Middleware as the
mitigation and scoped the issue to deployments without it. Here, for split
deployments, Edge Middleware is bypassed too, since the attacker reaches `/_isr`
directly and the middleware only sees `/_isr` while the origin runs none.

## Proof of concept
1. Create an Astro app with `output: 'server'` and adapter
   `vercel({ isr: true })`.
2. Add a page at `/admin` that returns sensitive content.
3. Deny `/admin` at the edge, for example a Vercel path rule that returns 403, or
   a middleware auth check in a split (`edgeMiddleware: true`) build.
4. Request `/admin`. It is blocked (403).
5. Request `/_isr?x_astro_path=/admin`. It returns 200 with the admin content.
   The response header `X-Vercel-Cache: MISS` confirms it was rendered fresh, not
   served from an existing cache entry.

## What is not affected
1. Classic (non split) middleware. It runs inside the origin against the rewritten
   path, so it still applies to the target route.
2. State changing requests. Vercel serves ISR functions for GET only, and returns
   403 for POST, PUT and DELETE, so the method preserving variant of CVE-2026-33768
   does not reproduce here. Impact is limited to reading (confidentiality).
3. Whole deployment protection (Vercel SSO or password), which also covers `/_isr`.

## Severity
Unauthenticated read of any GET rendered route that is protected only at the edge.
No integrity or availability impact because the vector is GET only.

## Suggested fix
One option would be to require the secret again for path overrides, the way
PR #15959 did, so the ISR branch stops trusting the client supplied `x_astro_path`.
The 404 that PR #16079 was fixing would then need another approach that does not
rely on client input.

## References
- https://github.com/withastro/astro/security/advisories/GHSA-mr6q-rp88-fx84
- https://github.com/withastro/astro/security/advisories/GHSA-x27w-589x-frm2
- https://github.com/withastro/astro/pull/16079
- https://github.com/withastro/astro/pull/17370
- https://github.com/withastro/astro/commit/3a43cf0f3690a8e33cb30109bc5165611cf38fcd
- https://github.com/withastro/astro/commit/aa266364fe9e105317b66e218fe04567307fb57f
- https://github.com/withastro/astro
- https://github.com/withastro/astro/releases/tag/@astrojs/vercel@11.0.3
