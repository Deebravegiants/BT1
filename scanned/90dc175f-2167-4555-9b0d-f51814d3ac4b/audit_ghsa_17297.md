# [M] axios-cache-interceptor Vulnerable to Cache Poisoning via Ignored HTTP Vary Header

## Summary
Severity: Medium
Advisory: GHSA-x4m5-4cw8-vc44
CVE: CVE-2025-69202
CWE: CWE-524, CWE-639
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-12-30
Source: https://github.com/advisories/GHSA-x4m5-4cw8-vc44
Type: github-advisory

## Affected
- npm: `axios-cache-interceptor` — affected >=0 <1.11.1

## Details
## Summary

When a server calls an upstream service using different auth tokens, axios-cache-interceptor returns incorrect cached responses, leading to authorization bypass.

## Details

The cache key is generated only from the URL, ignoring request headers like `Authorization`. When the server responds with `Vary: Authorization` (indicating the response varies by auth token), the library ignores this, causing all requests to share the same cache regardless of authorization.

## Impact

**Affected:** Server-side applications (APIs, proxies, backend services) that:

- Use axios-cache-interceptor to cache requests to upstream services
- Handle requests from multiple users with different auth tokens
- Upstream services replies on `Vary` to differentiate caches

**Not affected:** Browser/client-side applications (single user per browser session).

Services using different auth tokens to call upstream services will return incorrect cached data, bypassing authorization checks and leaking user data across different authenticated sessions.

## Solution

After `v1.11.1`, automatic `Vary` header support is now enabled by default.

When server responds with `Vary: Authorization`, cache keys now include the authorization header value. Each user gets their own cache.

```js
// v1.11.1+ (automatic, no config needed)
// User 123: key = hash(url + {authorization: 'Bearer 123'})
// User 456: key = hash(url + {authorization: 'Bearer 456'})
// ✓ Different caches, no poisoning
```

## Remediation

Upgrade to v1.11.1 or later. _No code changes required, protection is automatic_


## Proof of Concept

```js
const http = require('node:http');
const axios = require('axios');
const { setupCache } = require('axios-cache-interceptor');

// Server that returns different responses based on Authorization
const server = http.createServer((req, res) => {
  const auth = req.headers.authorization;

  res.setHeader('Vary', 'Authorization');

  if (auth === 'Bearer 123') {
    res.write('Hello, user 123!');
  } else if (auth === 'Bearer 456') {
    res.write('Hello, user 456!');
  } else {
    res.write('Unknown');
  }

  res.end();
});

server.listen(5000);

// Client making requests with different tokens
const cachedAxios = setupCache(axios.create());

const server2 = http.createServer(async (_req, res) => {
  const authHeader =
    Math.random() < 0.5 ? 'Bearer 123' : 'Bearer 456';

  const response = await cachedAxios.get('http://localhost:5000', {
    headers: { Authorization: authHeader }
  });

  console.log({
    response: response.data,
    cached: response.cached,
    auth: authHeader
  });
  res.write(response.data);
  res.end();
});

server2.listen(5001);

// Trigger 10 requests
Promise.all(
  Array.from({ length: 10 }, () =>
    axios.get('http://localhost:5001').catch(console.error)
  )
).finally(() => {
  server.close();
  server2.close();
});
```

All 10 responses return "Hello, user 123!" even when using "Bearer 456" - users receive each other's cached data.

## References
- https://github.com/arthurfiorette/axios-cache-interceptor/security/advisories/GHSA-x4m5-4cw8-vc44
- https://nvd.nist.gov/vuln/detail/CVE-2025-69202
- https://github.com/arthurfiorette/axios-cache-interceptor/commit/49a808059dfc081b9cc23d48f243d55dfce15f01
- https://github.com/arthurfiorette/axios-cache-interceptor
