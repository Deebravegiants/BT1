# [H] Angular: SSRF via protocol-relative and backslash URLs in Angular Platform-Server

## Summary
Severity: High
Advisory: GHSA-45q2-gjvg-7973
CVE: CVE-2026-41423
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-45q2-gjvg-7973
Type: github-advisory

## Affected
- npm: `@angular/platform-server` — affected >=22.0.0-next.0 <22.0.0-next.8
- npm: `@angular/platform-server` — affected >=21.0.0-next.0 <21.2.9
- npm: `@angular/platform-server` — affected >=20.0.0-next.0 <20.3.19
- npm: `@angular/platform-server` — affected >=19.0.0-next.0 <19.2.21
- npm: `@angular/platform-server` — affected >=0

## Details
### Impact

A [Server-Side Request Forgery (SSRF)](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/SSRF) vulnerability exists in `@angular/platform-server` due to improper handling of URLs during Server-Side Rendering (SSR).

When an attacker sends a request such as `GET /\evil.com/ HTTP/1.1` the server engine (Express, etc.) passes the URL string to Angular’s rendering functions.

Because the URL parser normalizes the backslash to a forward slash for HTTP/HTTPS schemes, the internal state of the application is hijacked to believe the current origin is `evil.com`. This misinterpretation tricks the application into treating the attacker’s domain as the local origin. Consequently, any relative `HttpClient` requests or `PlatformLocation.hostname` references are redirected to the attacker controlled server, potentially exposing internal APIs or metadata services.

**Affected APIs:**
- `renderModule`
- `renderApplication`
- `CommonEngine` (from `@angular/ssr`)

**Non-Affected APIs:**
- `AngularAppEngine` (from `@angular/ssr`)
- `AngularNodeAppEngine` (from `@angular/ssr`)

### Attack Preconditions
- The server has outbound network access.
- The application uses Angular SSR via the affected APIs.
- A pathname is passed as URL to the rendering method  (e.g. using `req.url`).
- The server-side code performs HTTP requests using `HttpClient` with relative URLs or uses `PlatformLocation.hostname` to build URLs. 


### Patches
- 22.0.0-next.8
- 21.2.9
- 20.3.19
- 19.2.21

### Workarounds
Developers should implement a middleware to sanitize the request URL before it reaches Angular. This involves stripping or normalizing leading slashes:

```js
app.use((req, res, next) => {
  // Sanitize the URL to ensure it starts with a single forward slash
  if (req.url.startsWith('//') || req.url.startsWith('/\\') || req.url.startsWith('\\')) {
     req.url = '/' + req.url.replace(/^[/\\]+/, '');
  }
  next();
});

```
### References
- [Fix](https://github.com/angular/angular/pull/68194)

## References
- https://github.com/angular/angular/security/advisories/GHSA-45q2-gjvg-7973
- https://nvd.nist.gov/vuln/detail/CVE-2026-41423
- https://github.com/angular/angular/pull/68194
- https://github.com/angular/angular/commit/ede7c58a2aa13fdccc8f0b67ce93ba1c11749412
- https://github.com/angular/angular
