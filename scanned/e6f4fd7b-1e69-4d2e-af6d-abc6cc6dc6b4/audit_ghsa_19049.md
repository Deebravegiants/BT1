# [M] Sentry's sensitive headers are leaked when `sendDefaultPii` is set to `true`

## Summary
Severity: Medium
Advisory: GHSA-6465-jgvq-jhgp
CVE: CVE-2025-65944
CWE: CWE-201
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:N/VI:N/VA:N/SC:H/SI:L/SA:L (CVSS_V4)
Published: 2025-11-24
Source: https://github.com/advisories/GHSA-6465-jgvq-jhgp
Type: github-advisory

## Affected
- npm: `@sentry/node` — affected >=10.11.0 <10.27.0
- npm: `@sentry/astro` — affected >=10.11.0 <10.27.0
- npm: `@sentry/aws-serverless` — affected >=10.11.0 <10.27.0
- npm: `@sentry/bun` — affected >=10.11.0 <10.27.0
- npm: `@sentry/google-cloud-serverless` — affected >=10.11.0 <10.27.0
- npm: `@sentry/nestjs` — affected >=10.11.0 <10.27.0
- npm: `@sentry/nextjs` — affected >=10.11.0 <10.27.0
- npm: `@sentry/node-core` — affected >=10.11.0 <10.27.0
- npm: `@sentry/nuxt` — affected >=10.11.0 <10.27.0
- npm: `@sentry/remix` — affected >=10.11.0 <10.27.0
- npm: `@sentry/solidstart` — affected >=10.11.0 <10.27.0
- npm: `@sentry/sveltekit` — affected >=10.11.0 <10.27.0

## Details
### Impact
In version 10.11.0, a change to how the SDK collects request data in Node.js applications caused certain incoming HTTP headers to be added as trace span attributes. When `sendDefaultPii: true` was set, a few headers that were previously redacted - including Authorization and Cookie - were unintentionally allowed through.

Sentry’s server-side scrubbing (handled by Sentry's Relay edge proxy) normally serves as a second layer of protection. However, because it relied on the same matching logic as the SDK, it also failed to catch these headers in this case.

Users may be impacted if:

1. Their Sentry SDK configuration has `sendDefaultPii` set to `true`
2. Their application uses one of the Node.js Sentry SDKs with version from `10.11.0` to `10.26.0` inclusively:
- @sentry/astro
- @sentry/aws-serverless
- @sentry/bun
- @sentry/google-cloud-serverless
- @sentry/nestjs
- @sentry/nextjs
- @sentry/node
- @sentry/node-core
- @sentry/nuxt
- @sentry/remix
- @sentry/solidstart
- @sentry/sveltekit

Users can check if their project was affected, by visiting Explore → Traces and searching for “http.request.header.authorization”, “http.request.header.cookie” or similar. Any potentially sensitive values will be specific to users' applications and configurations.

### Patches
The issue has been patched in all Sentry JavaScript SDKs starting from the [10.27.0](https://github.com/getsentry/sentry-javascript/releases/tag/10.27.0) version.

### Workarounds
Sentry strongly encourage customers to upgrade the SDK to the latest available version, [10.27.0](https://github.com/getsentry/sentry-javascript/releases/tag/10.27.0) or later.
If it is not possible, consider setting `sendDefaultPii: false` to avoid unintentionally sending sensitive headers. See [here](https://docs.sentry.io/platforms/javascript/guides/node/#step-2-configure) for documentation.

### Resources
* https://develop.sentry.dev/sdk/expected-features/data-handling/#sensitive-data
* https://github.com/getsentry/sentry-javascript/releases/tag/10.11.0
* https://github.com/getsentry/sentry-javascript/pull/17475
* https://docs.sentry.io/platforms/javascript/guides/node/data-management/data-collected/#cookies

## References
- https://github.com/getsentry/sentry-javascript/security/advisories/GHSA-6465-jgvq-jhgp
- https://nvd.nist.gov/vuln/detail/CVE-2025-65944
- https://github.com/getsentry/sentry-javascript/pull/17475
- https://github.com/getsentry/sentry-javascript/pull/18311
- https://github.com/getsentry/sentry-javascript/commit/a820fa2891fdcf985b834a5b557edf351ec54539
- https://github.com/getsentry/sentry-javascript
- https://github.com/getsentry/sentry-javascript/releases
- https://github.com/getsentry/sentry-javascript/releases/tag/10.11.0
- https://github.com/getsentry/sentry-javascript/releases/tag/10.27.0
