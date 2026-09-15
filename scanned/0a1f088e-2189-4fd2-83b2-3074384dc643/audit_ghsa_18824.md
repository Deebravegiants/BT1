# [H] Angular SSR has a Server-Side Request Forgery (SSRF) flaw

## Summary
Severity: High
Advisory: GHSA-q63q-pgmf-mxhr
CVE: CVE-2025-62427
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-16
Source: https://github.com/advisories/GHSA-q63q-pgmf-mxhr
Type: github-advisory

## Affected
- npm: `@angular/ssr` — affected >=19.0.0-next.0 <19.2.18
- npm: `@angular/ssr` — affected >=20.0.0-next.0 <20.3.6
- npm: `@angular/ssr` — affected >=21.0.0-next.0 <21.0.0-next.8

## Details
### Impact
The vulnerability is a **Server-Side Request Forgery (SSRF)** flaw within the URL resolution mechanism of Angular's Server-Side Rendering package (`@angular/ssr`).

The function `createRequestUrl` uses the native `URL` constructor. When an incoming request path (e.g., `originalUrl` or `url`) begins with a **double forward slash (`//`) or backslash (`\\`)**, the `URL` constructor treats it as a **schema-relative URL**. This behavior overrides the security-intended base URL (protocol, host, and port) supplied as the second argument, instead resolving the URL against the scheme of the base URL but adopting the attacker-controlled hostname.

This allows an attacker to specify an external domain in the URL path, tricking the Angular SSR environment into setting the page's virtual location (accessible via `DOCUMENT` or `PlatformLocation` tokens) to this attacker-controlled domain. Any subsequent **relative HTTP requests** made during the SSR process (e.g., using `HttpClient.get('assets/data.json')`) will be incorrectly resolved against the attacker's domain, forcing the server to communicate with an arbitrary external endpoint.

#### Exploit Scenario
A request to `http://localhost:4200//attacker-domain.com/some-page` causes Angular to believe the host is attacker-domain.com. A relative request to api/data then becomes a server-side request to `http://attacker-domain.com/api/data`.

### Patches

- `@angular/ssr` 19.2.18
- `@angular/ssr` 20.3.6
- `@angular/ssr` 21.0.0-next.8

## Mitigation

The application's internal location must be robustly determined from the incoming request. The fix requires sanitizing or validating the request path to prevent it from being interpreted as a schema-relative URL (i.e., ensuring it does not start with `//`).

#### Server-Side Middleware
If you can't upgrade to a patched version, implement a **middleware** on the Node.js/Express server that hosts the Angular SSR application to explicitly reject or sanitize requests where the path begins with a double slash (`//`).

**Example (Express/Node.js):**

```ts
// Place this middleware before the Angular SSR handler
app.use((req, res, next) => {
  if (req.originalUrl?.startsWith('//')) {
    // Sanitize by forcing a single slash
    req.originalUrl = req.originalUrl.replace(/^\/\/+/, '/');
    req.url = req.url.replace(/^\/\/+/, '/');
  }
  next();
});
```

### References

- Report: https://github.com/angular/angular-cli/issues/31464
- Fix:  https://github.com/angular/angular-cli/pull/31474

## References
- https://github.com/angular/angular-cli/security/advisories/GHSA-q63q-pgmf-mxhr
- https://nvd.nist.gov/vuln/detail/CVE-2025-62427
- https://github.com/angular/angular-cli/commit/5271547c80662de10cb3bcb648779a83f6efedfb
- https://github.com/angular/angular-cli
