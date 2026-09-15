# [H] ALPINE-CVE-2026-21710

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-21710
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-21710
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.22.2-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.22.2-r0
- Alpine:v3.23: `nodejs` — affected >=0 <24.14.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.14.1-r0

## Details
A flaw in Node.js HTTP request handling causes an uncaught `TypeError` when a request is received with a header named `__proto__` and the application accesses `req.headersDistinct`.

When this occurs, `dest["__proto__"]` resolves to `Object.prototype` rather than `undefined`, causing `.push()` to be called on a non-array. This exception is thrown synchronously inside a property getter and cannot be intercepted by `error` event listeners, meaning it cannot be handled without wrapping every `req.headersDistinct` access in a `try/catch`.

* This vulnerability affects all Node.js HTTP servers on **20.x, 22.x, 24.x, and v25.x**

## References
- https://security.alpinelinux.org/vuln/CVE-2026-21710
