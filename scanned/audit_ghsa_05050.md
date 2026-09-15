# [H] @angular/platform-server: URL Parser Differential leading to SSRF Allowlist Bypass

## Summary
Severity: High
Advisory: GHSA-xrxm-cp7j-8xf6
CVE: CVE-2026-50168
CWE: CWE-346, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-xrxm-cp7j-8xf6
Type: github-advisory

## Affected
- npm: `@angular/platform-server` — affected >=22.0.0-next.0 <22.0.0-rc.2
- npm: `@angular/platform-server` — affected >=20.0.0-next.0 <20.3.22
- npm: `@angular/platform-server` — affected >=19.0.0-next.0 <19.2.23
- npm: `@angular/platform-server` — affected >=0
- npm: `@angular/platform-server` — affected >=21.0.0-next.0 <21.2.15

## Details
An issue in the `@angular/platform-server` package allows remote attackers to bypass host allowlist constraints and direct server-side outgoing requests to arbitrary external endpoints. This occurs due to a parser differential between the strict WHATWG URL parser used for allowlist validation and the lenient Domino URL parser used to initialize the server emulated DOM.

When a server-side request contains a malformed URL with a double port structure (e.g., `http://evil.com:80:80/path`), Node's strict `URL.canParse(url)` logic returns `false` and skips host check validation entirely. However, the same malformed URL is later accepted and parsed leniently by Domino's internal parser, which resolves the origin to `http://evil.com:80`. The Angular SSR HTTP request interceptor (`relativeUrlsTransformerInterceptorFn`) then resolves all relative backend HTTP requests against this adopted origin, executing the SSRF attack.

### Impact

Any Angular application utilizing server-side rendering (`@angular/platform-server`) that configures host routing allowlists (`allowedHosts`) is vulnerable to this allowlist bypass. 

By sending an HTTP request with a malformed Host header (e.g. `Host: evil.com:80:80`) or an absolute-form request URI, an attacker can bypass the allowlist logic completely (even when configured with a strict default deny setup). The SSR application will then route all relative `HttpClient` outgoing API queries—which commonly carry sensitive credentials, session cookies, and internal authorization tokens—to the attacker-controlled server instead of the intended backend services. Additionally, the attacker can supply custom payloads back to the emulated DOM, leading to response injection and content poisoning within the rendered HTML served to users.

### Attack Preconditions

To successfully exploit this vulnerability, the following environment parameters and application states must all concurrently exist:

1. **Active Server-Side Rendering (SSR):** The application must be configured to run with Angular Server-Side Rendering (`@angular/platform-server`).
2. **Host Header/URI Propagation:** The SSR handler must reconstruct the request URL using raw client inputs (such as request Host headers or absolute-form URIs) and pass it as `config.url` to the rendering API (`renderApplication` or `renderModule`).
3. **Outbound Relative HTTP Requests:** The server application must perform outbound backend API requests using relative paths (e.g., `this.http.get('/api/data')`) that undergo base-URL interceptor rewriting.
4. **Enabled Allowed Hosts Check:** The server must use the framework-provided `allowedHosts` options to limit valid server locations.

### Patches

* 22.0.0-rc.2
* 21.2.15
* 20.3.22
* 19.2.23

## References
- https://github.com/angular/angular/security/advisories/GHSA-xrxm-cp7j-8xf6
- https://nvd.nist.gov/vuln/detail/CVE-2026-50168
- https://github.com/angular/angular/pull/68928
- https://github.com/angular/angular
