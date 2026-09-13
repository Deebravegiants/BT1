# [H] @angular/common: Information Leak via Default Caching of Credentialed Requests in HttpTransferCache

## Summary
Severity: High
Advisory: GHSA-q6f4-qqrg-jv6x
CVE: CVE-2026-50170
CWE: CWE-524
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-q6f4-qqrg-jv6x
Type: github-advisory

## Affected
- npm: `@angular/common` — affected >=22.0.0-next.0 <22.0.0-rc.2
- npm: `@angular/common` — affected >=20.0.0-next.0 <20.3.22
- npm: `@angular/common` — affected >=19.0.0-next.0 <19.2.23
- npm: `@angular/common` — affected >=0
- npm: `@angular/common` — affected >=21.0.0-next.0 <21.2.15

## Details
A vulnerability was discovered in `@angular/common` when Server-Side Rendering (SSR) and hydration are enabled. The `HttpTransferCache` utility optimizes hydration by caching outgoing HTTP requests performed during SSR and transferring the cached state to the client-side application via `TransferState`.

However, the caching mechanism fails to inspect the `withCredentials` flag or the `Cookie` header of outgoing requests. As a result, credentialed, user-specific responses may be cached by default in the shared `TransferState` payload. When these responses are serialized into the HTML, any caching layer (such as a CDN, reverse proxy, or shared server cache) that caches the SSR-rendered HTML page could inadvertently cache and leak one user's private data to other users, leading to a high-severity information disclosure vulnerability.

### Impact

Successful exploitation allows an unauthenticated attacker to obtain sensitive, user-specific information of other authenticated users. This occurs when:

* The SSR-rendered HTML containing the cached private data is stored in a shared cache (e.g., CDN, reverse proxy).  
* Subsequent requests for the same page receive the cached HTML containing the first user's private data.

### Attack Preconditions

* **SSR and Hydration Enabled:** The Angular application must be configured to use Server-Side Rendering and hydration (e.g., using `provideClientHydration()`).  
* **Credentialed Requests during SSR:** The application must perform HTTP requests that require user-specific authentication (using cookies or `withCredentials: true`) during the initial server-side render.  
* **Shared Caching:** The application's HTML responses must be cached by a shared caching layer (CDN, reverse proxy, or server-side cache) without proper cache-control headers to distinguish authenticated users.

### Patches
- 22.0.0-rc.2
- 21.2.15
- 20.3.22
- 19.2.23

## References
- https://github.com/angular/angular/security/advisories/GHSA-q6f4-qqrg-jv6x
- https://nvd.nist.gov/vuln/detail/CVE-2026-50170
- https://github.com/angular/angular/pull/67964
- https://github.com/angular/angular
