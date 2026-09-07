# [M] @angular/service-worker: Request Credential & Cache Policy Stripping

## Summary
Severity: Medium
Advisory: GHSA-95qp-cmmw-mgqv
CVE: CVE-2026-50184
CWE: CWE-200, CWE-524
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-95qp-cmmw-mgqv
Type: github-advisory

## Affected
- npm: `@angular/service-worker` — affected >=22.0.0-next.0 <22.0.0-rc.2
- npm: `@angular/service-worker` — affected >=21.0.0-next.0 <21.2.15
- npm: `@angular/service-worker` — affected >=20.0.0-next.0 <20.3.22
- npm: `@angular/service-worker` — affected >=19.0.0-next.0 <19.2.23
- npm: `@angular/service-worker` — affected >=0

## Details
An issue in the `@angular/service-worker` package compromises the integrity of request-policy enforcement during request reconstruction. When the Angular Service Worker intercepts network requests for matched assets, it reconstructs a new `Request` object using an internal helper function.

During this reconstruction process, the helper function strips explicit client-defined safety parameters: the credentials configuration (such as `credentials: 'omit'`) and the HTTP `cache` mode configuration (such as `cache: 'no-store'`). These are reverted back to standard browser-default parameters (`credentials: 'same-origin'` and default HTTP cache properties).

This causes the browser to include active credentials (such as cookies or Authorization headers) on outbound requests where the client-side developer explicitly instructed they should be omitted, leading to potential session leaks. Additionally, it causes private or non-cacheable resources to be cached by the service worker's engine, making private page states accessible or persistent inside the client's local cache post-logout.

### Impact
Web applications registering the `@angular/service-worker` package are vulnerable to credential exposure or post-logout cache persistence if client-side code relies on fetch calls with explicit safety attributes (such as `{ credentials: 'omit' }` or `{ cache: 'no-store' }`) targeting paths matched by service worker asset groups. 

By stripping these safety boundaries, the service worker exposes same-origin cookies and dynamic sensitive data to endpoints that should not receive them, or retains dynamic user sessions in cache storage where logout operations fail to fully evict user records.

### Attack Preconditions
To successfully exploit this vulnerability, all of the following application states and parameters must concurrently exist:
1. **Active Angular Service Worker:** The target application uses `@angular/service-worker` and has an active registration of `ngsw-worker.js` inside the client's browser context.
2. **Asset Group Matching:** An `assetGroups` pattern in `ngsw-config.json` encompasses the target dynamic routing endpoint.
3. **Established User Session:** The victim user currently has an active authentication state, such as valid same-origin session cookies or auth headers stored by the browser.
4. **Client-Side Safe Fetch Call:** The application initiates an explicit fetch request to the route with safety parameters: `{ credentials: 'omit' }` or specific cache control parameters (e.g. `{ cache: 'no-store' }`).

### Mitigations & Workarounds
If upgrading the `@angular/service-worker` package is not immediately feasible, developers should implement the following defensive measures:
* **Strict Cookie Configuration:** Apply strict flags to session cookies (`SameSite=Strict; Secure; HttpOnly`) and ensure complete route isolation for credential-guarded secure resources.
* **Exclude Secure Endpoints from SW Config:** Ensure that patterns targeting dynamic, secure endpoints are explicitly excluded from automatic asset groups or caching scopes in your `ngsw-config.json`.
* **Post-Logout Cache Invalidation:** Programmatically purge the browser's Cache Storage API entries registered by the Angular Service Worker upon user logout:
  ```javascript
  if ('caches' in window) {
    caches.keys().then(names => {
      for (let name of names) {
        if (name.startsWith('ngsw:')) {
          caches.delete(name);
        }
      }
    });
  }
  ```
### Patches
- 22.0.0-rc.2
- 21.2.15
- 20.3.22
- 19.2.23

## References
- https://github.com/angular/angular/security/advisories/GHSA-95qp-cmmw-mgqv
- https://nvd.nist.gov/vuln/detail/CVE-2026-50184
- https://github.com/angular/angular/pull/68904
- https://github.com/angular/angular
