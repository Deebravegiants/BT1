# [H] Sending a GET or HEAD request with a body crashes SvelteKit

## Summary
Severity: High
Advisory: GHSA-g5m6-hxpp-fc49
CVE: CVE-2024-23641
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-01-24
Source: https://github.com/advisories/GHSA-g5m6-hxpp-fc49
Type: github-advisory

## Affected
- npm: `@sveltejs/kit` — affected >=2.0.0 <2.4.3
- npm: `@sveltejs/adapter-node` — affected >=2.0.0 <2.1.2
- npm: `@sveltejs/adapter-node` — affected >=3.0.0 <3.0.3
- npm: `@sveltejs/adapter-node` — affected >=4.0.0 <4.0.1

## Details
### Summary
In SvelteKit 2 sending a GET request with a body eg `{}` to a SvelteKit app in preview or with `adapter-node` throws `Request with GET/HEAD method cannot have body.` and crashes the app.

```
node:internal/deps/undici/undici:6066
          throw new TypeError("Request with GET/HEAD method cannot have body.");
                ^

TypeError: Request with GET/HEAD method cannot have body.
    at new Request (node:internal/deps/undici/undici:6066:17)
    at getRequest (file:///C:/Users/admin/Desktop/reproduction/node_modules/@sveltejs/kit/src/exports/node/index.js:107:9)
    at file:///C:/Users/admin/Desktop/reproduction/node_modules/@sveltejs/kit/src/exports/vite/preview/index.js:181:26
    at call (file:///C:/Users/admin/Desktop/reproduction/node_modules/vite/dist/node/chunks/dep-9A4-l-43.js:44795:7)
    at next (file:///C:/Users/admin/Desktop/reproduction/node_modules/vite/dist/node/chunks/dep-9A4-l-43.js:44739:5)
    at file:///C:/Users/admin/Desktop/reproduction/node_modules/@sveltejs/kit/src/exports/vite/preview/index.js:172:6
    at call (file:///C:/Users/admin/Desktop/reproduction/node_modules/vite/dist/node/chunks/dep-9A4-l-43.js:44795:7)
    at next (file:///C:/Users/admin/Desktop/reproduction/node_modules/vite/dist/node/chunks/dep-9A4-l-43.js:44739:5)
    at file:///C:/Users/admin/Desktop/reproduction/node_modules/@sveltejs/kit/src/exports/vite/preview/index.js:211:27
    at call (file:///C:/Users/admin/Desktop/reproduction/node_modules/vite/dist/node/chunks/dep-9A4-l-43.js:44795:7)

Node.js v20.11.0
```

`TRACE` requests will also cause the app to crash. Prerendered pages and SvelteKit 1 apps are not affected.

<!--
### Details
_Give all details on the vulnerability. Pointing to the incriminated source code is very helpful for the maintainer._
-->
### PoC
<!-- _Complete instructions, including specific configuration details, to reproduce the vulnerability._ -->
First do a fresh install of SvelteKit 2 with the example app. Typescript.

1. `npm run build`
2. `npm run preview`
3. Go to http://localhost:4173 (works)
4. curl -X GET -d "{}" http://localhost:4173/bye
5. Application crashes and http://localhost:4173 is down

### Impact
<!-- _What kind of vulnerability is it? Who is impacted?_ -->
Denial of Service for apps using `adapter-node`

## References
- https://github.com/sveltejs/kit/security/advisories/GHSA-g5m6-hxpp-fc49
- https://nvd.nist.gov/vuln/detail/CVE-2024-23641
- https://github.com/sveltejs/kit/commit/af34142631c876a7eb62ff81f71e8a3f90dafee9
- https://github.com/sveltejs/kit
