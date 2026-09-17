# [C] Angular SSR is vulnerable to SSRF and Header Injection via request handling pipeline

## Summary
Severity: Critical
Advisory: GHSA-x288-3778-4hhx
CVE: CVE-2026-27739
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N (CVSS_V4)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-x288-3778-4hhx
Type: github-advisory

## Affected
- npm: `@angular/ssr` — affected >=21.2.0-next.0 <21.2.0-rc.1
- npm: `@angular/ssr` — affected >=21.0.0-next.0 <21.1.5
- npm: `@angular/ssr` — affected >=20.0.0-next.0 <20.3.17
- npm: `@angular/ssr` — affected >=0 <19.2.21
- npm: `@nguniversal/common` — affected >=0
- npm: `@nguniversal/express-engine` — affected >=0

## Details
A [Server-Side Request Forgery (SSRF)](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/SSRF) vulnerability has been identified in the Angular SSR request handling pipeline. The vulnerability exists because Angular’s internal URL reconstruction logic directly trusts and consumes user-controlled HTTP headers specifically the Host and `X-Forwarded-*` family to determine the application's base origin without any validation of the destination domain.

Specifically, the framework didn't have checks for the following:
- **Host Domain**: The `Host` and `X-Forwarded-Host` headers were not checked to belong to a trusted origin. This allows an attacker to redefine the "base" of the application to an arbitrary external domain.
- **Path & Character Sanitization**: The `X-Forwarded-Host` header was not checked for path segments or special characters, allowing manipulation of the base path for all resolved relative URLs.
- **Port Validation**: The `X-Forwarded-Port` header was not verified as numeric, leading to malformed URI construction or injection attacks.


This vulnerability manifests in two primary ways:

- **Implicit Relative URL Resolution**: Angular's `HttpClient` resolves relative URLs against this unvalidated and potentially malformed base origin. An attacker can "steer" these requests to an external server or internal service.
- **Explicit Manual Construction**: Developers injecting the `REQUEST` object to manually construct URLs (for fetch or third-party SDKs) directly inherit these unsanitized values. By accessing the `Host` / `X-Forwarded-*` headers, the application logic may perform requests to attacker-controlled destinations or malformed endpoints.

### Impact

When successfully exploited, this vulnerability allows for arbitrary internal request steering. This can lead to:
- **Credential Exfiltration**: Stealing sensitive `Authorization` headers or session cookies by redirecting them to an attacker's server.
- **Internal Network Probing**: Accessing and transmitting data from internal services, databases, or cloud metadata endpoints (e.g., `169.254.169.254`) not exposed to the public internet.
- Confidentiality Breach: Accessing sensitive information processed within the application's server-side context.

### Attack Preconditions

- The victim application must use Angular SSR (Server-Side Rendering).
- The application must perform `HttpClient` requests using relative URLs OR manually construct URLs using the unvalidated `Host` / `X-Forwarded-*` headers using the `REQUEST` object.
- **Direct Header Access**: The application server is reachable by an attacker who can influence these headers without strict validation from a front-facing proxy.
- **Lack of Upstream Validation**: The infrastructure (Cloud, CDN, or Load Balancer) does not sanitize or validate incoming headers.

### Patches

- 21.2.0-rc.1
- 21.1.5
- 20.3.17
- 19.2.21


### Workarounds
- **Use Absolute URLs:** Avoid using `req.headers` for URL construction. Instead, use trusted variables for your base API paths.
- **Implement Strict Header Validation (Middleware)**: If you cannot upgrade immediately, implement a middleware in your `server.ts` to enforce numeric ports and validated hostnames.

```ts
const ALLOWED_HOSTS = new Set(['your-domain.com']);

app.use((req, res, next) => {
  const hostHeader = (req.headers['x-forwarded-host'] ?? req.headers['host'])?.toString();
  const portHeader = req.headers['x-forwarded-port']?.toString();

  if (hostHeader) {
    const hostname = hostHeader.split(':')[0];
    // Reject if hostname contains path separators or is not in allowlist
    if (/^[a-z0-9.:-]+$/i.test(hostname) || 
       (!ALLOWED_HOSTS.has(hostname) && hostname !== 'localhost')) {
      return res.status(400).send('Invalid Hostname');
    }
  }

  // Ensure port is strictly numeric if provided
  if (portHeader && !/^\d+$/.test(portHeader)) {
    return res.status(400).send('Invalid Port');
  }

  next();
});
```

### References

- [Fix](https://github.com/angular/angular-cli/pull/32516)
- [Docs](https://angular.dev/best-practices/security#preventing-server-side-request-forgery-ssrf)

## References
- https://github.com/angular/angular-cli/security/advisories/GHSA-x288-3778-4hhx
- https://nvd.nist.gov/vuln/detail/CVE-2026-27739
- https://github.com/angular/angular-cli/pull/32516
- https://angular.dev/best-practices/security#preventing-server-side-request-forgery-ssrf
- https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/SSRF
- https://github.com/angular/angular-cli
