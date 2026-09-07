# [M] Astro: composable `astro/hono` pipeline bypasses `security.checkOrigin` when `middleware()` is absent or misordered

## Summary
Severity: Medium
Advisory: GHSA-8mv7-9c27-98vc
CVE: CVE-2026-73423
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-8mv7-9c27-98vc
Type: github-advisory

## Affected
- npm: `astro` — affected >=7.0.0 <7.0.6

## Details
## Summary

In the composable `astro/hono` pipeline, the `security.checkOrigin` protection is only installed by the `middleware()` primitive. The `actions()` and `pages()` primitives each dispatch to user code independently, so a pipeline that mounts either primitive before (or without) `middleware()` will bypass the origin check for those requests.

## Details

`security.checkOrigin` (default: `true`) is intended to reject cross-site `POST`/`PUT`/`PATCH`/`DELETE` form submissions. In the classic pipeline (`astro()` all-in-one), the check always runs because Astro injects a virtual middleware module even when the user has no `src/middleware.ts`. In the composable `astro/hono` pipeline, the user assembles primitives manually. The check is only installed inside `middleware()` — so:

- Mounting `actions()` before `middleware()` allows cross-origin form-encoded action requests to execute before the gate runs. The `examples/advanced-routing` example and the Cloudflare `hono` docs shipped this order.
- Omitting `middleware()` entirely (reasonable for apps with no custom middleware) silently drops `checkOrigin` protection for all on-demand endpoints and pages dispatched through `pages()`.

The attack is a blind write-only CSRF: the attacker can trigger a state-mutating action or endpoint handler using the victim's cookies, but cannot read the cross-origin response body.

## Affected versions

Astro `>= 7.0.0` when using the composable `astro/hono` pipeline with either:
- `actions()` mounted before `middleware()`, or
- `pages()` used without `middleware()`

The default (non-composable) pipeline is not affected.

## Fix

The origin check is now applied at each dispatch sink (`ActionHandler.handle` and `PagesHandler.handleWithErrorFallback`), gated on `manifest.checkOrigin`, using the same predicate as the middleware. The check is order-independent and a no-op when `middleware()` has already run.

Fix: https://github.com/withastro/astro/pull/17250

## Workaround

Ensure `middleware()` is mounted before both `actions()` and `pages()` in the composable pipeline, and that it is always included even when no custom middleware logic is needed:

```ts
app.use(middleware());
app.use(actions());
app.use(pages());
```

## References
- https://github.com/withastro/astro/security/advisories/GHSA-8mv7-9c27-98vc
- https://github.com/withastro/astro/pull/17250
- https://github.com/withastro/astro/commit/0b30b35f864310bee8485c952d1877e82e2b9b1a
- https://github.com/withastro/astro
- https://github.com/withastro/astro/releases/tag/astro@7.0.6
