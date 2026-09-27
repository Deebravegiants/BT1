# [M] Astro's middleware authentication checks based on url.pathname can be bypassed via url encoded values

## Summary
Severity: Medium
Advisory: GHSA-ggxq-hp9w-j794
CVE: CVE-2025-64765
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-19
Source: https://github.com/advisories/GHSA-ggxq-hp9w-j794
Type: github-advisory

## Affected
- npm: `astro` — affected >=0 <5.15.8

## Details
A mismatch exists between how Astro normalizes request paths for routing/rendering and how the application’s middleware reads the path for validation checks. Astro internally applies `decodeURI()` to determine which route to render, while the middleware uses `context.url.pathname` without applying the same normalization (decodeURI).

This discrepancy may allow attackers to reach protected routes (e.g., /admin) using encoded path variants that pass routing but bypass validation checks.

https://github.com/withastro/astro/blob/ebc4b1cde82c76076d5d673b5b70f94be2c066f3/packages/astro/src/vite-plugin-astro-server/request.ts#L40-L44

```js
/** The main logic to route dev server requests to pages in Astro. */
export async function handleRequest({
    pipeline,
    routesList,
    controller,
    incomingRequest,
    incomingResponse,
}: HandleRequest) {
    const { config, loader } = pipeline;
    const origin = `${loader.isHttps() ? 'https' : 'http'}://${
        incomingRequest.headers[':authority'] ?? incomingRequest.headers.host
    }`;

    const url = new URL(origin + incomingRequest.url);
    let pathname: string;
    if (config.trailingSlash === 'never' && !incomingRequest.url) {
        pathname = '';
    } else {
        // We already have a middleware that checks if there's an incoming URL that has invalid URI, so it's safe
        // to not handle the error: packages/astro/src/vite-plugin-astro-server/base.ts
        pathname = decodeURI(url.pathname); // here this url is for routing/rendering
    }

    // Add config.base back to url before passing it to SSR
    url.pathname = removeTrailingForwardSlash(config.base) + url.pathname; // this is used for middleware context
```

Consider an application having the following middleware code:

```js
import { defineMiddleware } from "astro/middleware";

export const onRequest = defineMiddleware(async (context, next) => {
  const isAuthed = false;  // simulate no auth
  if (context.url.pathname === "/admin" && !isAuthed) {
    return context.redirect("/");
  }
  return next();
});
```

`context.url.pathname` is validated , if it's equal to `/admin` the `isAuthed` property must be true for the next() method to be called. The same example can be found in the official docs https://docs.astro.build/en/guides/authentication/


`context.url.pathname` returns the raw version which is `/%61admin` while pathname which is used for routing/rendering `/admin`, this creates a path normalization mismatch.

By sending the following request, it's possible to bypass the middleware check

```
GET /%61dmin HTTP/1.1
Host: localhost:3000
```

<img width="1920" height="1025" alt="image" src="https://github.com/user-attachments/assets/7e0eeecd-607a-4c73-b12e-5977a30c9bc4" />


**Remediation**

Ensure middleware context has  the same normalized pathname value that Astro uses internally, because any difference could allow it to bypass such checks. In short maybe something like this

```diff
        pathname = decodeURI(url.pathname);
    }

    // Add config.base back to url before passing it to SSR
-    url.pathname = removeTrailingForwardSlash(config.base) + url.pathname;
+    url.pathname = removeTrailingForwardSlash(config.base) + decodeURI(url.pathname);
```

Thank you, let @Sudistark know if any more info is needed. Happy to help :)

## References
- https://github.com/withastro/astro/security/advisories/GHSA-ggxq-hp9w-j794
- https://nvd.nist.gov/vuln/detail/CVE-2025-64765
- https://github.com/withastro/astro/commit/6f800813516b07bbe12c666a92937525fddb58ce
- https://github.com/withastro/astro
