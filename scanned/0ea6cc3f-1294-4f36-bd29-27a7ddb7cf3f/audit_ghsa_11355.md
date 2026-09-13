# [H] Clerk: SSRF in the opt-in clerkFrontendApiProxy feature may leak secret keys to unintended host

## Summary
Severity: High
Advisory: GHSA-gjxx-92w9-8v8f
CVE: CVE-2026-34076
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-gjxx-92w9-8v8f
Type: github-advisory

## Affected
- npm: `@clerk/backend` — affected >=3.0.0 <3.2.3
- npm: `@clerk/express` — affected >=2.0.0 <2.0.7
- npm: `@clerk/hono` — affected >=0.1.0 <0.1.5
- npm: `@clerk/fastify` — affected >=3.1.0 <3.1.5

## Details
## Summary

The `clerkFrontendApiProxy` function in `@clerk/backend` is vulnerable to Server-Side Request Forgery (SSRF). An unauthenticated attacker can craft a request path that causes the proxy to send the application's `Clerk-Secret-Key` to an attacker-controlled server.

## Affected packages

Only applications that have opted into the `frontendApiProxy` feature are affected. This feature is not enabled by default. **Users of `@clerk/nextjs` are not affected** due to how the framework handles repeated `/` in request paths.

| Package | Affected versions | Fixed version |
|---|---|---|
| `@clerk/backend` | `>= 3.0.0, <= 3.2.2` | `3.2.3` |
| `@clerk/express` | `>= 2.0.0, <= 2.0.6` | `2.0.7` |
| `@clerk/hono` | `>= 0.1.0, <= 0.1.4` | `0.1.5` |
| `@clerk/fastify` | `>= 3.1.0, <= 3.1.4` | `3.1.5` |

Search your codebase for the `frontendApiProxy` option. If none of the patterns below appear in your code, you are not affected.

**@clerk/express**
```ts
app.use(clerkMiddleware({ frontendApiProxy: { enabled: true } }));
```

**@clerk/hono**
```ts
app.use('*', clerkMiddleware({ frontendApiProxy: { enabled: true } }));
```

**@clerk/fastify**
```ts
fastify.register(clerkPlugin, { frontendApiProxy: { enabled: true } });
```

**@clerk/backend**
```ts
import { clerkFrontendApiProxy } from '@clerk/backend/proxy';
```

A quick way to check across your entire project:

```sh
grep -r "frontendApiProxy\|clerkFrontendApiProxy" .
```

If there are no matches, you are not using this feature.


## Recommended actions

Clerk's internal logs show no evidence of users utilizing the built-in proxy with the impacted versions. Despite that, if you are on an impacted version and use the built-in proxy we recommend upgrading and rotating your Clerk Secret Key immediately.

1. **Upgrade** to the patched version of `@clerk/backend` (and `@clerk/express`, `@clerk/hono`, etc.)
2. **Rotate your Clerk Secret Key** after upgrading - if an attacker exploited this vulnerability, they may have captured your key. Rotate it in the [Clerk Dashboard](https://dashboard.clerk.com) under **API Keys**.  You should deploy your application with the updated key before revoking the existing key.
3. **Audit access logs** for requests to your proxy endpoint (`/__clerk/` by default) containing double slashes in the path.



## Credit

Discovered during an internal code audit.

## References
- https://github.com/clerk/javascript/security/advisories/GHSA-gjxx-92w9-8v8f
- https://nvd.nist.gov/vuln/detail/CVE-2026-34076
- https://github.com/clerk/javascript
