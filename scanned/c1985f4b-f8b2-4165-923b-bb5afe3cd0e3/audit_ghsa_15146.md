# [M] @hono/node-server cannot handle "double dots" in URL

## Summary
Severity: Medium
Advisory: GHSA-rjq5-w47x-x359
CVE: CVE-2024-23340
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-01-23
Source: https://github.com/advisories/GHSA-rjq5-w47x-x359
Type: github-advisory

## Affected
- npm: `@hono/node-server` — affected >=1.3.0 <1.4.1

## Details
### Impact

Since v1.3.0, we use our own Request object. This is great, but the `url` behavior is unexpected.

In the standard API, if the URL contains `..`, here called "double dots", the URL string returned by Request will be in the resolved path.

```ts
const req = new Request('http://localhost/static/../foo.txt') // Web-standards
console.log(req.url) // http://localhost/foo.txt
```

However, the `url` in our Request does not resolve double dots, so `http://localhost/static/.. /foo.txt` is returned.

```ts
const req = new Request('http://localhost/static/../foo.txt')
console.log(req.url) // http://localhost/static/../foo.txt
```

It will pass unresolved paths to the web application. This causes vulnerabilities like #123 when using `serveStatic`.

Note: Modern web browsers and a latest `curl` command resolve double dots on the client side, so it does not affect you if the user uses them. However, problems may occur if accessed by a client that does not resolve them.

### Patches

"v1.4.1" includes the change to fix this issue.

### Workarounds

Don't use `serveStatic`.

## References
- https://github.com/honojs/node-server/security/advisories/GHSA-rjq5-w47x-x359
- https://nvd.nist.gov/vuln/detail/CVE-2024-23340
- https://github.com/honojs/node-server/commit/dd9b9a9b23e3896403c90a740e7f1f0892feb402
- https://github.com/honojs/node-server
- https://github.com/honojs/node-server/blob/8cea466fd05e6d2e99c28011fc0e2c2d3f3397c9/src/request.ts#L43-L45
