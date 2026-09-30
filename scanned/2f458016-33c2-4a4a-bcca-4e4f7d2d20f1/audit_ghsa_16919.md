# [H] @hono/node-server has Denial of Service risk when receiving Host header that cannot be parsed

## Summary
Severity: High
Advisory: GHSA-hgxw-5xg3-69jx
CVE: CVE-2024-32652
CWE: CWE-755
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-19
Source: https://github.com/advisories/GHSA-hgxw-5xg3-69jx
Type: github-advisory

## Affected
- npm: `@hono/node-server` — affected >=1.3.0 <1.10.1

## Details
### Impact

The application hangs when receiving a Host header with a value that `@hono/node-server` can't handle well. Invalid values are those that cannot be parsed by the `URL` as a hostname such as an empty string, slashes `/`, and other strings.

For example, if you have a simple application:

```ts
import { serve } from '@hono/node-server'
import { Hono } from 'hono'

const app = new Hono()

app.get('/', (c) => c.text('Hello'))

serve(app)
```

Sending a request with a Host header with an empty value to it:

```
curl localhost:3000/ -H "Host: "
```

The results:

```
node:internal/url:775
    this.#updateContext(bindingUrl.parse(input, base));
                                   ^

TypeError: Invalid URL
    at new URL (node:internal/url:775:36)
    at newRequest (/Users/yusuke/work/h/159/node_modules/@hono/node-server/dist/index.js:137:17)
    at Server.<anonymous> (/Users/yusuke/work/h/159/node_modules/@hono/node-server/dist/index.js:399:17)
    at Server.emit (node:events:514:28)
    at Server.emit (node:domain:488:12)
    at parserOnIncoming (node:_http_server:1143:12)
    at HTTPParser.parserOnHeadersComplete (node:_http_common:119:17) {
  code: 'ERR_INVALID_URL',
  input: 'http:///'
}
```

### Patches

The version `1.10.1` includes the fix for this issue. But, you should use `1.11.0`, which has other fixes related to this issue. https://github.com/honojs/node-server/issues/160 https://github.com/honojs/node-server/issues/161

### Workarounds

Nothing. Upgrade your `@hono/node-server`.

### References

https://github.com/honojs/node-server/issues/159

## References
- https://github.com/honojs/node-server/security/advisories/GHSA-hgxw-5xg3-69jx
- https://nvd.nist.gov/vuln/detail/CVE-2024-32652
- https://github.com/honojs/node-server/issues/159
- https://github.com/honojs/node-server/issues/161
- https://github.com/honojs/node-server/commit/306d98f02a8671a0a1fb91ac8fe7e281690c05af
- https://github.com/honojs/node-server/commit/d847e60249fd8183ba0998bc379ba20505643204
- https://github.com/honojs/node-server
