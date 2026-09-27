# [H] Angular: Cache-Key Ambiguity in HttpTransferCache Leading to Cross-Request Response Reuse and State Poisoning

## Summary
Severity: High
Advisory: GHSA-jhpw-976m-542j
CVE: CVE-2026-68945
CWE: CWE-345
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-jhpw-976m-542j
Type: github-advisory

## Affected
- npm: `@angular/common` — affected >=22.0.0-next.0 <22.0.2
- npm: `@angular/common` — affected >=21.0.0-next.0 <21.2.19
- npm: `@angular/common` — affected >=20.0.0-next.0 <20.3.27
- npm: `@angular/common` — affected >=0

## Details
Angular's `HttpTransferCache` caches HTTP requests made during Server-Side Rendering (SSR) so that they can be reused during client-side hydration.

During SSR, `HttpTransferCache` previously generated identical key material for distinct request parameters when repeated values were present because repeated values were joined with commas:

```ts
new HttpParams().set('role', 'user,admin')
new HttpParams().append('role', 'user').append('role', 'admin')
```

Both requests previously serialized as `role=user,admin`, allowing distinct `HttpClient` requests to produce the same transfer-cache key material.

### Impact

In an SSR application, this cache-key ambiguity can make a later security-sensitive `HttpClient` request receive the response from an earlier semantically different request in the same render. For example, an attacker-influenced scalar-comma request can be cached and then replayed as the response for a trusted repeated-param authorization or data request to the same URL. As a result, Angular's server-rendered output can be based on the wrong backend response because the trusted request is not dispatched. This can lead to:

- **State Poisoning**: Using incorrect or attacker-influenced cached responses for subsequent application logic.
- **Cross-Request Response Reuse**: Reusing cached responses across requests with semantically different parameters.

### Patched Versions

- 22.0.2
- 21.2.19
- 20.3.27

### Workarounds

If you cannot upgrade immediately, configure your `HttpClient` requests to skip transfer caching for sensitive endpoints where repeated parameter keys are used:

```ts
this.http.get('/api/resource', {
  transferCache: false
});
```

Alternatively, disable the HTTP transfer cache globally in your application bootstrap config:

```ts
import { provideClientHydration, withNoHttpTransferCache } from '@angular/platform-browser';

export const appConfig = {
  providers: [
    provideClientHydration(
      withNoHttpTransferCache()
    )
  ]
};
```

## References
- https://github.com/angular/angular/security/advisories/GHSA-jhpw-976m-542j
- https://github.com/angular/angular/pull/68571
- https://github.com/angular/angular/commit/6867f77ec779a0a24f6339ad6c775f444202103c
- https://github.com/angular/angular/commit/948a8d6831e8920b54663ec79421da95210e0e35
- https://github.com/angular/angular/commit/a64e2883e9dc4abdac70209129be303de79e5b2b
- https://github.com/angular/angular/commit/a6c7fc5c13e6e494a4c9bd8e773b8d4b2a99b20c
- https://github.com/angular/angular
