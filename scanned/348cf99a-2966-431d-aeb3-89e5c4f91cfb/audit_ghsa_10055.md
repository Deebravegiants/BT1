# [H] Clerk has an authorization bypass when combining organization, billing, or reverification checks

## Summary
Severity: High
Advisory: GHSA-w24r-5266-9c3c
CVE: CVE-2026-42349
CWE: CWE-754, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-30
Source: https://github.com/advisories/GHSA-w24r-5266-9c3c
Type: github-advisory

## Affected
- npm: `@clerk/shared` — affected >=3.0.0 <3.47.5
- npm: `@clerk/shared` — affected >=4.0.0 <4.8.3
- npm: `@clerk/backend` — affected >=2.0.0 <2.33.3
- npm: `@clerk/backend` — affected >=3.0.0 <3.2.14
- npm: `@clerk/nextjs` — affected >=6.0.0 <6.39.3
- npm: `@clerk/nextjs` — affected >=7.0.0 <7.2.4
- npm: `@clerk/clerk-js` — affected >=5.22.0 <5.125.10
- npm: `@clerk/clerk-js` — affected >=6.0.0 <6.7.5
- npm: `@clerk/clerk-react` — affected >=5.9.0 <5.61.6
- npm: `@clerk/react` — affected >=6.0.0 <6.4.3
- npm: `@clerk/vue` — affected >=1.0.0 <1.17.21
- npm: `@clerk/vue` — affected >=2.0.0 <2.0.16
- npm: `@clerk/astro` — affected >=2.0.0 <2.17.11
- npm: `@clerk/astro` — affected >=3.0.0 <3.0.18
- npm: `@clerk/nuxt` — affected >=1.0.0 <1.13.29
- npm: `@clerk/nuxt` — affected >=2.0.0 <2.2.5
- npm: `@clerk/clerk-expo` — affected >=2.2.11 <2.19.36
- npm: `@clerk/expo` — affected >=3.0.0 <3.2.2
- npm: `@clerk/react-router` — affected >=0.0.1 <2.4.13
- npm: `@clerk/react-router` — affected >=3.0.0 <3.1.4
- npm: `@clerk/tanstack-react-start` — affected >=0.0.1 <0.29.11
- npm: `@clerk/tanstack-react-start` — affected >=1.0.0 <1.1.4
- npm: `@clerk/chrome-extension` — affected >=1.3.5 <2.9.15
- npm: `@clerk/chrome-extension` — affected >=3.0.0 <3.1.15
- npm: `@clerk/fastify` — affected >=1.0.42 <2.6.31
- npm: `@clerk/fastify` — affected >=3.0.0 <3.1.16
- npm: `@clerk/express` — affected >=0.1.0 <1.7.79
- npm: `@clerk/express` — affected >=2.0.0 <2.1.6
- npm: `@clerk/hono` — affected >=0.0.2 <0.1.16

## Details
### Summary

`has()`, `auth.protect()`, and related authorization predicates in `@clerk/shared`, `@clerk/nextjs`, `@clerk/backend`, and other framework SDKs can return true for certain combined authorization checks when the result should be false, allowing a gated action to proceed for a user who does not satisfy the full set of requested conditions.

Sessions are not compromised and no existing user can be impersonated. The bypass is limited to the authorization decision returned by the predicate. `clerkMiddleware` continues to authenticate requests correctly, `auth()` reflects the real authentication state, and token verification is unaffected.

### Who is affected

All apps that combine more than one authorization dimension in a single `has()` or `auth.protect()` call should upgrade to the patched versions. Patches are drop-in with no API changes. The information below describes the scope of the bypass and helps developers understand whether their apps are potentially affected, but is not a reason to delay the upgrade.

This call shape can be bypassed if certain conditions are met: a `has()` or `auth.protect()` call that combines a `reverification` check with any of `role`, `permission`, `feature`, or `plan`, or that combines a billing check (`feature` or `plan`) with a role or permission check.


```ts
// Reverification combined with role / permission / feature / plan
await auth.protect({ permission: 'org:settings:delete', reverification: 'strict' });
const canAct = has({ role: 'org:admin', reverification: 'strict' });

// Billing (feature / plan) combined with role / permission
const canAct = has({ permission: 'org:admin', feature: 'premium' });
```

Single-condition checks are not affected and continue to fail closed as expected:

```ts
await auth.protect({ permission: 'org:settings:delete' });
has({ reverification: 'strict' });
```

The callback form of `auth.protect` is not affected unless the callback itself invokes one of the affected shapes:

```ts
await auth.protect(has => has({ permission: 'org:X' }) && has({ reverification: 'strict' }));
```

App patterns that rely only on single-condition checks, or that combine them via the callback form, are unaffected. Authentication, session state, and token verification continue to work correctly regardless of this bypass.

`@clerk/shared` is usually not imported directly in application code, but the fix lives there and reaches an app through its framework package. If developers import `createCheckAuthorization` from `@clerk/shared` directly, their apps are also affected. Run `npm why @clerk/shared` (or the app's package manager's equivalent) to check the installed version.

### Additional `auth.protect()` bypass

A second, related bypass lives in `@clerk/nextjs`: `auth.protect()` silently discarded authorization params (`role`, `permission`, `feature`, `plan`, `reverification`) whenever the same argument object also contained `unauthenticatedUrl`, `unauthorizedUrl`, or `token`.

### Recommended actions

Upgrade to the latest patch release of the consuming app's framework package on its current major. Both Core 2 and Core 3 release lines have patches. See the "Affected packages" section above for the exact vulnerable ranges and patched versions per package.

If a consuming app pins `@clerk/clerk-js` directly, upgrade it to the patched version. Most apps load `@clerk/clerk-js` from Clerk's CDN through their framework package and will receive the fix automatically, with no upgrade step required.

### Workaround

If developers cannot upgrade immediately, split combined `has()` or `auth.protect()` calls into sequential single-condition checks:

```ts
// Replace
await auth.protect({ permission: 'org:X', reverification: 'strict' });
// With
await auth.protect({ reverification: 'strict' });
await auth.protect({ permission: 'org:X' });
```

Each single-condition check fails closed as expected, so evaluating them independently and denying if either fails produces the correct result.

### Timeline

This issue was reported on 18 APR 2026, patched on 22 APR 2026, and publicly disclosed on 22 APR 2026.

Thanks to AISafe for the responsible disclosure of this vulnerability.

## References
- https://github.com/clerk/javascript/security/advisories/GHSA-w24r-5266-9c3c
- https://nvd.nist.gov/vuln/detail/CVE-2026-42349
- https://github.com/clerk/javascript
