# [M] Angular Service Worker Policy-Bypass & Credential-Stripping Vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-gv2q-mqqv-365m
CVE: CVE-2026-50169
CWE: CWE-200, CWE-441, CWE-524
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-gv2q-mqqv-365m
Type: github-advisory

## Affected
- npm: `@angular/service-worker` — affected >=22.0.0-next.0 <22.0.0-rc.2
- npm: `@angular/service-worker` — affected >=20.0.0-next.0 <20.3.22
- npm: `@angular/service-worker` — affected >=19.0.0-next.0 <19.2.23
- npm: `@angular/service-worker` — affected >=0
- npm: `@angular/service-worker` — affected >=21.0.0-next.0 <21.2.15

## Details
An issue in the `@angular/service-worker` package compromises the integrity of request-policy enforcement during request reconstruction. When the Angular Service Worker intercepts network requests for matched assets, it reconstructs a new `Request` object using an internal helper function. 

During this reconstruction process, the helper function strips the strict, client-defined request redirect policy configuration (such as `redirect: 'error'`), falling back to the browser's default `'follow'` strategy.

If the target web application makes client-side requests with a strict policy (e.g., expecting a network error instead of automatically following redirects), the service worker will bypass this instruction and automatically follow HTTP 3xx redirects to other destinations. This acts as an unintended proxy/intermediary ("Confused Deputy") and can result in cookie/credential exposure or same-origin session-restricted data leakage if public dynamic routes redirect to sensitive routes.

### Impact
Web applications registering the `@angular/service-worker` package are vulnerable to this redirect-policy bypass if they make safe client-side fetch calls (such as `{ redirect: 'error' }`) to paths matched by a service worker asset group (such as lazy-loaded JavaScript bundles or dynamic public assets) that can return HTTP redirects to authenticated same-origin secure endpoints. 

By stripping developer-defined safety boundaries, the service worker allows the browser to transparently query and return data from credentials-guarded resources that should have been blocked at the network barrier.

### Attack Preconditions
To successfully exploit this vulnerability, all of the following application states and parameters must concurrently exist:
1. **Active Angular Service Worker:** The target application uses `@angular/service-worker` and has an active registration of `ngsw-worker.js` inside the client's browser context.
2. **Asset Group Matching:** An `assetGroups` pattern in `ngsw-config.json` encompasses the target dynamic routing endpoint.
3. **Same-Origin Dynamic Redirection:** The server routes a public matched asset route to a service that returns an HTTP 3xx redirect pointing to a sensitive, session-restricted same-origin private route (e.g., `/private/account-summary.json`).
4. **Established User Session:** The victim user currently has an active authentication state, such as valid same-origin session cookies or auth headers stored by the browser.
5. **Client-Side Safe Fetch Call:** The application initiates an explicit fetch request to the route with safety parameters: `{ redirect: 'error' }`.

### Mitigations & Workarounds
If upgrading the `@angular/service-worker` package is not immediately feasible, developers should implement the following defensive measures:
* **Avoid Public-to-Private Dynamic Redirection:** Refactor the server architecture so that public paths matched by service worker asset groups never issue HTTP 3xx redirects to authenticated same-origin secure endpoints.
* **Strict Cookie Configuration:** Apply strict flags to session cookies (`SameSite=Strict; Secure; HttpOnly`) and consider explicit route isolations (such as subdomains) for credential-guarded private resources.
* **Exclude Secure Endpoints from SW Config:** Verify your `ngsw-config.json` settings and ensure that patterns targeting dynamic, secure endpoints are explicitly excluded from automatic asset groups or caching scopes.

### Patches
- 22.0.0-rc.2
- 21.2.15
- 20.3.22
- 19.2.23

## References
- https://github.com/angular/angular/security/advisories/GHSA-gv2q-mqqv-365m
- https://nvd.nist.gov/vuln/detail/CVE-2026-50169
- https://github.com/angular/angular/pull/67494
- https://github.com/angular/angular
