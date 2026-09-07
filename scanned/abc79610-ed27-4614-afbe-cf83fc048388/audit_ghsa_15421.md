# [H] Nuxt Icon affected by a Server-Side Request Forgery (SSRF)

## Summary
Severity: High
Advisory: GHSA-cxgv-px37-4mp2
CVE: CVE-2024-42352
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-cxgv-px37-4mp2
Type: github-advisory

## Affected
- npm: `@nuxt/icon` — affected >=0 <1.4.5

## Details
### Summary
`nuxt/icon` provides an API to allow client side icon lookup. This endpoint is at `/api/_nuxt_icon/[name]`.

The proxied request path is improperly parsed, allowing an attacker to change the scheme and host of the request. This leads to SSRF, and could potentially lead to sensitive data exposure.

### Details
The `new URL` constructor is used to parse the final path. This constructor can be passed a relative scheme or path in order to change the host the request is sent to. This constructor is also very tolerant of poorly formatted URLs.

As a result we can pass a path prefixed with the string `http:`. This has the effect of changing the scheme to HTTP. We can then subsequently pass a new host, for example `http:127.0.0.1:8080`. This would allow us to send requests to a local server. 

### PoC
Make a request to `/api/_nuxt_icon/http:example.com`, observe the data returned has been fetched from a different resource than intended. 

I typically try to find an example within Nuxt infrastructure that is vulnerable to these types of bugs, but I could not identify any with this endpoint enabled.

### Impact
+ SSRF, potential sensitive data exposure.
+ I do not believe this can be chained into an XSS, but it may be possible.
+ Does not have a security impact on services deployed on Cloudflare Workers.
+ Does not impact certain builds and modes (like static builds).
+ Can be mitigated using by disabling the `fallbackToApi` option.

### Fix
+ Ensure the host has not been changed after the path is parsed.
+ Alternatively, prefix the path with `./`.

## References
- https://github.com/nuxt/icon/security/advisories/GHSA-cxgv-px37-4mp2
- https://nvd.nist.gov/vuln/detail/CVE-2024-42352
- https://github.com/nuxt/icon/commit/4564518c2b2ed8235a7715056ccdfce96ca3d0ff
- https://github.com/nuxt/icon
