# [M] Nitro has a proxy scope bypass via percent-encoded path traversal in `routeRules`

## Summary
Severity: Medium
Advisory: GHSA-5w89-w975-hf9q
CVE: CVE-2026-44373
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-5w89-w975-hf9q
Type: github-advisory

## Affected
- npm: `nitro` — affected >=0 <3.0.260429-beta
- npm: `nitropack` — affected >=0 <2.13.4

## Details
A proxy route rule like:

```ts
routeRules: {
  "/api/orders/**": { proxy: { to: "http://upstream/orders/**" } }
}
```

is intended to limit the proxy to URLs under `/api/orders/`. Before the patch, an attacker could bypass that scope by sending percent-encoded path traversal (`..%2f`) in the URL, causing Nitro to forward a request that the upstream resolved outside the configured scope. Example exploit:

```
GET /api/orders/..%2fadmin%2fconfig.json
```

Nitro sees `..%2f` as opaque characters at match time, the `/api/orders/**` rule matched, and the raw path was forwarded to the upstream as `/orders/..%2fadmin/config.json`. An upstream that decodes `%2F` to  `/` then resolved `..` and can serve `/admin/config.json` outside the intended scope.

### Are you affected?

Users may be affected if **ALL** of the following are true:

1. Their project uses Nitro's `routeRules` with a `proxy` entry (`{ proxy: { to: "..." } }`).
2. The proxy `to` value uses a `/**` wildcard suffix to forward sub-paths.
3. The **upstream** behind the proxy decodes `%2F` as `/` before routing or filesystem lookup.
4. Proxy route rules are _not_ handled natively at CDN (nitro v3 and vercel)

Whether the bypass actually leaks data depends on the upstream. Modern JS frameworks keep `%2F` opaque per RFC 3986 and are safe by construction. 

- **Safe examples:** H3 v2, Express v5, Hono v4 — modern JS frameworks keep `%2F` opaque per RFC 3986.
- **Vulnerable examples:** naive imlementations that decodes the URL, static file servers, CGI dispatchers, Python `os.path`-based routing, anything sitting behind another layer that decodes `%2F` (common in microservice meshes).

## Impact

Any HTTP path reachable from the Nitro server to the upstream could be requested, regardless of the configured `/**` scope. In typical deployments (API gateway, BFF, microservice proxy) this could expose internal admin endpoints, secrets endpoints, or other services the developer believed the scope rule fenced off.

## Patched versions

Upgrade to one of:

- [2.13.4](https://github.com/nitrojs/nitro/releases/tag/v2.13.4) or later (https://github.com/nitrojs/nitro/pull/4223) 
- [3.0.260429-beta](https://github.com/nitrojs/nitro/releases/tag/v3.0.260429-beta) or later (https://github.com/nitrojs/nitro/pull/4222)

The fix canonicalizes the incoming pathname before building the upstream URL and rejects requests with `400 Bad Request` if the resolved path would escape the rule's base. The bytes forwarded upstream are unchanged when the request is allowed.

> Note: the fix assumes the upstream does not double-decode percent-encoding. If your upstream decodes twice (`%252F → %2F → /`), it remains your responsibility to harden it. **Single-decode is standard**.

## Credits

Reported by [@mHe4am](https://github.com/mHe4am) ([@he4am on HackerOne](https://hackerone.com/he4am)) via the [Vercel Open Source](https://hackerone.com/vercel-open-source?type=team) program.

## References
- https://github.com/nitrojs/nitro/security/advisories/GHSA-5w89-w975-hf9q
- https://nvd.nist.gov/vuln/detail/CVE-2026-44373
- https://github.com/nitrojs/nitro/pull/4222
- https://github.com/nitrojs/nitro/pull/4223
- https://github.com/nitrojs/nitro
- https://github.com/nitrojs/nitro/releases/tag/v2.13.4
- https://github.com/nitrojs/nitro/releases/tag/v3.0.260429-beta
