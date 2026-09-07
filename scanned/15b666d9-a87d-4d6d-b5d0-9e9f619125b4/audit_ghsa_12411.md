# [M] Vite XSS vulnerability in `server.transformIndexHtml` via URL payload

## Summary
Severity: Medium
Advisory: GHSA-92r3-m2mg-pj97
CVE: CVE-2023-49293
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-12-05
Source: https://github.com/advisories/GHSA-92r3-m2mg-pj97
Type: github-advisory

## Affected
- npm: `vite` — affected >=4.4.0 <4.4.12
- npm: `vite` — affected >=4.5.0 <4.5.1
- npm: `vite` — affected >=5.0.0 <5.0.5

## Details
### Summary
When Vite's HTML transformation is invoked manually via `server.transformIndexHtml`, the original request URL is passed in unmodified, and the `html` being transformed contains inline module scripts (`<script type="module">...</script>`), it is possible to inject arbitrary HTML into the transformed output by supplying a malicious URL query string to `server.transformIndexHtml`.

### Impact
Only apps using `appType: 'custom'` and using the default Vite HTML middleware are affected. The HTML entry must also contain an inline script. The attack requires a user to click on a malicious URL while running the dev server. Restricted files aren't exposed to the attacker.

### Patches
Fixed in vite@5.0.5, vite@4.5.1, vite@4.4.12

### Details
Suppose `index.html` contains an inline module script:

```html
<script type="module">
  // Inline script
</script>
```

This script is transformed into a proxy script like

```html
<script type="module" src="/index.html?html-proxy&index=0.js"></script>
```

due to Vite's HTML plugin:

https://github.com/vitejs/vite/blob/7fd7c6cebfcad34ae7021ebee28f97b1f28ef3f3/packages/vite/src/node/plugins/html.ts#L429-L465

When `appType: 'spa' | 'mpa'`, Vite serves HTML itself, and `htmlFallbackMiddleware` rewrites `req.url` to the canonical path of `index.html`,

https://github.com/vitejs/vite/blob/73ef074b80fa7252e0c46a37a2c94ba8cba46504/packages/vite/src/node/server/middlewares/htmlFallback.ts#L44-L47

so the `url` passed to `server.transformIndexHtml` is `/index.html`.

However, if `appType: 'custom'`, HTML is served manually, and if `server.transformIndexHtml` is called with the unmodified request URL (as the SSR docs suggest), then the path of the transformed `html-proxy` script varies with the request URL. For example, a request with path `/` produces

```html
<script type="module" src="/@id/__x00__/index.html?html-proxy&index=0.js"></script>
```

It is possible to abuse this behavior by crafting a request URL to contain a malicious payload like

```
"></script><script>alert('boom')</script>
```

so a request to http://localhost:5173/?%22%3E%3C/script%3E%3Cscript%3Ealert(%27boom%27)%3C/script%3E produces HTML output like

```html
<script type="module" src="/@id/__x00__/?"></script><script>alert("boom")</script>?html-proxy&index=0.js"></script>
```

which demonstrates XSS.

### PoC

- Example 1. Serving HTML from `vite dev` middleware with `appType: 'custom'`
    - Go to https://stackblitz.com/edit/vitejs-vite-9xhma4?file=main.js&terminal=dev-html
    - "Open in New Tab"
    - Edit URL to set query string to `?%22%3E%3C/script%3E%3Cscript%3Ealert(%27boom%27)%3C/script%3E` and navigate
    - Witness XSS:
    - ![image](https://user-images.githubusercontent.com/2456381/287434281-13757894-7a63-4a73-b1e9-d2b024c19d14.png)
- Example 2. Serving HTML from SSR-style Express server (Vite dev server runs in middleware mode):
    - Go to https://stackblitz.com/edit/vitejs-vite-9xhma4?file=main.js&terminal=server
    - (Same steps as above)
- Example 3. Plain `vite dev` (this shows that vanilla `vite dev` is _not_ vulnerable, provided `htmlFallbackMiddleware` is used)
    - Go to https://stackblitz.com/edit/vitejs-vite-9xhma4?file=main.js&terminal=dev
    - (Same steps as above)
    - You should _not_ see the alert box in this case

### Detailed Impact

This will probably predominantly affect [development-mode SSR](https://vitejs.dev/guide/ssr#setting-up-the-dev-server), where `vite.transformHtml` is called using the original `req.url`, per the docs:

https://github.com/vitejs/vite/blob/7fd7c6cebfcad34ae7021ebee28f97b1f28ef3f3/docs/guide/ssr.md?plain=1#L114-L126

However, since this vulnerability affects `server.transformIndexHtml`, the scope of impact may be higher to also include other ad-hoc calls to `server.transformIndexHtml` from outside of Vite's own codebase.

My best guess at bisecting which versions are vulnerable involves the following test script

```js
import fs from 'node:fs/promises';
import * as vite from 'vite';

const html = `
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
  </head>
  <body>
    <script type="module">
      // Inline script
    </script>
  </body>
</html>
`;
const server = await vite.createServer({ appType: 'custom' });
const transformed = await server.transformIndexHtml('/?%22%3E%3C/script%3E%3Cscript%3Ealert(%27boom%27)%3C/script%3E', html);
console.log(transformed);
await server.close();
```

and using it I was able to narrow down to #13581. If this is correct, then vulnerable Vite versions are 4.4.0-beta.2 and higher (which includes 4.4.0).

## References
- https://github.com/vitejs/vite/security/advisories/GHSA-92r3-m2mg-pj97
- https://nvd.nist.gov/vuln/detail/CVE-2023-49293
- https://github.com/vitejs/vite
