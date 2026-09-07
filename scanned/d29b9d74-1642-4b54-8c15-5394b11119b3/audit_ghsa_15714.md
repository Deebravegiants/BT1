# [M] @jmondi/url-to-png enables capture screenshot of localhost web services (unauthenticated pages)

## Summary
Severity: Medium
Advisory: GHSA-342q-2mc2-5gmp
CVE: CVE-2024-39919
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-07-15
Source: https://github.com/advisories/GHSA-342q-2mc2-5gmp
Type: github-advisory

## Affected
- npm: `@jmondi/url-to-png` — affected >=0 <2.1.2

## Details
### Summary

The maintainer been contemplating whether FTP or other protocols could serve as useful functionalities, but there may not be a practical reason for it since we are utilizing headless Chrome to capture screenshots. The argument is based on the assumption that this package can function as a service.

The package includes an `ALLOW_LIST` where the host can specify which services the user is permitted to capture screenshots of. By default, capturing screenshots of web services running on localhost, 127.0.0.1, or the [::] is allowed.

The maintainer is of the opinion that the package should also have a blacklist due to a potential vulnerability (or rather design oversight). If someone hosts this on a server, users could then capture screenshots of other web services running locally.

Unless this is strictly for web pages. Something similar here: https://github.com/follow-redirects/follow-redirects/issues/235 (localhost is intended for end users or hosts to deny, and the package is for HTTP/HTTPS.)

This is marked as a `LOW` since the maintainer is not sure if this is a vulnerability, but it's still best to highlight it. :) 

### PoC

Have a service like so running locally:

```js
const http = require("http")

const server = http.createServer((req, res) => {
  console.log("Received headers:", req.headers)
  res.writeHead(200, { "Content-Type": "text/plain" })
  res.end("Something private! But Hello from Server 2 :)")
})

server.listen(3001, () => {
  console.log("Server two running on http://localhost:3001")
})
```

Run the package in dev mode, `pnpm dev`. Feed these URLs:

```
http://localhost:3089/?url=http://[::]:3001&width=4000
http://localhost:3089/?url=http://localhost:3001&width=4000
http://localhost:3089/?url=http://127.0.01:3001&width=4000
```

<img width="622" alt="image" src="https://github.com/jasonraimondi/url-to-png/assets/42532003/21f1c883-ba00-4a15-83b8-922484fa4c2b">



### Impact
Disclose internal web services?

## References
- https://github.com/jasonraimondi/url-to-png/security/advisories/GHSA-342q-2mc2-5gmp
- https://nvd.nist.gov/vuln/detail/CVE-2024-39919
- https://github.com/jasonraimondi/url-to-png/commit/f62ff40403ffa1781459d6be8d97b8035888c00c
- https://github.com/jasonraimondi/url-to-png
