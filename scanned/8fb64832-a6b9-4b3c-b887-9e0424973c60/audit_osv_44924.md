# [M] Angular: Information Leak via `HttpTransferCache` Bypass When Using `withRequestsMadeViaParent`

## Summary
Severity: Medium
Advisory: CVE-2026-88059
Aliases: GHSA-p297-fm68-3q8c
CVSS: 4.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88059
Type: osv

## Details
Angular is a development platform for building mobile and desktop web applications using TypeScript/JavaScript and other languages. Prior to 20.3.28, 21.2.20, and 22.1.1, Angular's @angular/common HttpTransferCache can cache an authenticated response when Server-Side Rendering (SSR) and hydration use a hierarchical HttpClient configured with withRequestsMadeViaParent. The child TransferCache evaluates an initially anonymous request before delegation, then a parent withInterceptors chain adds an Authorization header, cookie, or API token; although the parent cache skips the authenticated request, the child still stores the private response in TransferState serialized as JSON in the ng-state script. Exploitation requires provideClientHydration, child provideHttpClient delegation through withRequestsMadeViaParent, parent-level credential injection, and an SSR HTML response shared across users by a CDN, reverse proxy, or application cache. A later unauthenticated or unauthorized visitor can receive the cached HTML containing the earlier authenticated user's sensitive response data. Applications can mitigate by attaching credentials at the child, filtering sensitive endpoints with withHttpTransferCacheOptions, disabling transfer caching for sensitive routes, or marking personalized HTML private or no-store. This issue is fixed in versions 20.3.28, 21.2.20, and 22.1.1.

## References
- https://github.com/angular/angular/releases/tag/v20.3.28
- https://github.com/angular/angular/releases/tag/v21.2.20
- https://github.com/angular/angular/releases/tag/v22.1.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88059.json
- https://github.com/angular/angular/security/advisories/GHSA-p297-fm68-3q8c
- https://nvd.nist.gov/vuln/detail/CVE-2026-88059
- https://github.com/angular/angular/issues/69777
- https://github.com/angular/angular/commit/c45028e44f5f3c1e0006eaccf86642deca51b2af
- https://github.com/angular/angular/commit/caf616670fd20d528aa69e0131cc17d60f0cc27d
- https://github.com/angular/angular/commit/e4c416c20a1cb222ce73d29c035452b257380c56
- https://github.com/angular/angular/pull/69778
