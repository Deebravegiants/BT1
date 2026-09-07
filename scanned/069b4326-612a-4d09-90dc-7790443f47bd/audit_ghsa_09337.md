# [H] @angular/platform-server: SSRF via Hostname Hijacking

## Summary
Severity: High
Advisory: GHSA-rfh7-fxqc-q52v
CVE: CVE-2026-46417
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-rfh7-fxqc-q52v
Type: github-advisory

## Affected
- npm: `@angular/platform-server` — affected >=22.0.0-next.0 <22.0.0-next.12
- npm: `@angular/platform-server` — affected >=21.0.0-next.0 <21.2.13
- npm: `@angular/platform-server` — affected >=20.0.0-next.0 <20.3.21
- npm: `@angular/platform-server` — affected >=19.0.0-next.0 <19.2.22
- npm: `@angular/platform-server` — affected >=0

## Details
### Impact

A Server-Side Request Forgery (SSRF) vulnerability exists in `@angular/platform-server`. The issue stems from how the server-side rendering (SSR) engine processes the request URL provided to the rendering entry points.

When an absolute-form URL (e.g., `http://evil.com`) is passed to the rendering engine, the internal `ServerPlatformLocation` can be manipulated into adopting the attacker-controlled domain as the "current" hostname.

Consequently, any relative `HttpClient` requests or `PlatformLocation.hostname` references are redirected to the attacker controlled server, potentially exposing internal APIs or metadata services.

### Fix Information
The vulnerability is mitigated by introducing an Allowlist Mechanism directly into the core rendering APIs.
The renderModule and renderApplication functions now include an allowedHosts configuration option. The rendering engine validates the hostname extracted from the request URL against this list before proceeding. If the hostname does not match an allowed entry, the engine prevents the hostname hijacking, ensuring that HttpClient requests remain restricted to trusted domains.


### Patches
- 22.0.0-next.12
- 21.2.13
- 20.3.21
- 19.2.22


### Workarounds
Developers unable to update immediately should implement strict URL validation in their server entry point (e.g., `server.ts`). Ensure that `req.url` is validated against a known list of trusted hostnames or normalized to a relative path before being passed to`renderApplication` or `renderModule`.

```TypeScript
// Example manual normalization in Express
app.get('*', (req, res, next) => {
  const trustedHost = 'localhost:4000';
  // Ensure the request target matches expectations
  if (req.headers.host !== trustedHost) {
     return res.status(403).send('Forbidden');
  }
  next();
});
```

## References
- https://github.com/angular/angular/security/advisories/GHSA-rfh7-fxqc-q52v
- https://nvd.nist.gov/vuln/detail/CVE-2026-46417
- https://github.com/angular/angular/pull/68570
- https://access.redhat.com/security/cve/CVE-2026-46417
- https://bugzilla.redhat.com/show_bug.cgi?id=2491444
- https://github.com/angular/angular
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46417.json
