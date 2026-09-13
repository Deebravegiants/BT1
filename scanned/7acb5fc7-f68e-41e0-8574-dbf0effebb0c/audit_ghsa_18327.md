# [H] Angular SSR: Global Platform Injector Race Condition Leads to Cross-Request Data Leakage

## Summary
Severity: High
Advisory: GHSA-68x2-mx4q-78m7
CVE: CVE-2025-59052
CWE: CWE-362
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-10
Source: https://github.com/advisories/GHSA-68x2-mx4q-78m7
Type: github-advisory

## Affected
- npm: `@angular/platform-server` — affected >=16.0.0-next.0 <18.2.14
- npm: `@angular/platform-server` — affected >=20.0.0-next.0 <20.3.0
- npm: `@angular/platform-server` — affected >=19.0.0-next.0 <19.2.15
- npm: `@angular/platform-server` — affected >=21.0.0-next.0 <21.0.0-next.3
- npm: `@angular/ssr` — affected >=17.0.0-next.0 <18.2.21
- npm: `@angular/ssr` — affected >=19.0.0-next.0 <19.2.16
- npm: `@angular/ssr` — affected >=20.0.0-next.0 <20.3.0
- npm: `@angular/ssr` — affected >=21.0.0-next.0 <21.0.0-next.3
- npm: `@nguniversal/common` — affected >=16.0.0-next.0

## Details
### Impact

Angular uses a DI container (the "platform injector") to hold request-specific state during server-side rendering. For historical reasons, the container was stored as a JavaScript module-scoped global variable. When multiple requests are processed concurrently, they could inadvertently share or overwrite the global injector state.

In practical terms, this can lead to one request responding with data meant for a completely different request, leaking data or tokens included on the rendered page or in response headers. As long as an attacker had network access to send any traffic that received a rendered response, they may have been able to send a large number of requests and then inspect the responses for information leaks.

The following APIs were vulnerable and required SSR-only breaking changes:

* `bootstrapApplication`: This function previously implicitly retrieved the last platform injector that was created. It now requires an explicit `BootstrapContext` in a server environment. This function is only used for standalone applications. NgModule-based applications are not affected.
* `getPlatform`: This function previously returned the last platform instance that was created. It now always returns `null` in a server environment.
* `destroyPlatform`: This function previously destroyed the last platform instance that was created. It's now a no-op when called in a server environment.

For `bootstrapApplication`, the framework now provides a new argument to the application's bootstrap function:

```ts
// Before:
const bootstrap = () => bootstrapApplication(AppComponent, config);

// After:
const bootstrap = (context: BootstrapContext) =>
  bootstrapApplication(AppComponent, config, context);
```

As is usually the case for changes to Angular, an automatic schematic will take care of these code changes as part of ng update:

```sh
# For apps on Angular v20:
ng update @angular/cli @angular/core

# For apps on Angular v19:
ng update @angular/cli@19 @angular/core@19

# For apps on Angular v18:
ng update @angular/cli@18 @angular/core@18
```

The schematic can also be invoked explicitly if the version bump was pulled in independently:

```sh
# For apps on Angular v20:
ng update @angular/core --name add-bootstrap-context-to-server-main

# For apps on Angular v19:
ng update @angular/core@19 --name add-bootstrap-context-to-server-main

# For apps on Angular v18:
ng update @angular/core@18 --name add-bootstrap-context-to-server-main
```

For applications that still use `CommonEngine`, the `bootstrap` property in `CommonEngineOptions` also gains the same `context` argument in the patched versions of Angular.

In local development (`ng serve`), Angular CLI triggered a codepath for Angular's "JIT" feature on the server even in applications that weren't using it in the browser. The codepath introduced async behavior between platform creation and application bootstrap, triggering the race condition even if an application didn't explicitly use `getPlatform` or custom async logic in `bootstrap`. Angular applications should never run in this mode outside of local development.

### Patches

The issue has been patched in [all active release lines](https://angular.dev/reference/releases#actively-supported-versions) as well as in the v21 prerelease:

* `@angular/platform-server`: 21.0.0-next.3
* `@angular/platform-server`: 20.3.0
* `@angular/platform-server`: 19.2.15
* `@angular/platform-server:` 18.2.14

* `@angular/ssr`: 21.0.0-next.3
* `@angular/ssr`: 20.3.0
* `@angular/ssr`: 19.2.16
* `@angular/ssr`: 18.2.21

### Workarounds

* Disable SSR via [Server Routes](https://angular.dev/guide/ssr#server-routing) (v19+) or builder options.
* Remove any asynchronous behavior from custom `bootstrap` functions.
* Remove uses of `getPlatform()` in application code.
* Ensure that the server build defines `ngJitMode` as false.

### References

* https://github.com/angular/angular/pull/63562
* https://github.com/angular/angular-cli/pull/31108

## References
- https://github.com/angular/angular/security/advisories/GHSA-68x2-mx4q-78m7
- https://nvd.nist.gov/vuln/detail/CVE-2025-59052
- https://github.com/angular/angular-cli/pull/31108
- https://github.com/angular/angular/pull/63562
- https://github.com/angular/angular
