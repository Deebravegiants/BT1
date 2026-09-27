# [M] CVE-2026-15075

## Summary
Severity: Medium
Advisory: CVE-2026-15075
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-15075
Type: osv

## Details
In Eclipse Vert.x versions up to and including 4.5.29 (4.x branch) and 5.1.4 (5.x branch), DefaultRedirectHandler (vertx-core) propagates all request headers as-is across cross-origin HTTP 30x redirects. Only Content-Length is stripped; no origin comparison (scheme, host, port) is performed before copying headers to the redirect target.
As a result, credential headers, including Authorization, Cookie, Proxy-Authorization, and arbitrary custom headers such as X-API-Token, are forwarded to the redirect destination without the caller's knowledge.




An attacker who can cause a Vert.x HttpClient to issue a request that is redirected to an attacker-controlled host (for example, by supplying a URL to a webhook dispatcher, image proxy, or microservice URL fetcher) can capture bearer tokens, basic-auth credentials, session cookies, and API keys attached to the original request.

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/161
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15075.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15075
- https://github.com/eclipse-vertx/vert.x
