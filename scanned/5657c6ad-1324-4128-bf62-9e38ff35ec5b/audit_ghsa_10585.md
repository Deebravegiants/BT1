# [M] RedwoodSDK has Same-site CSRF through lack of origin validation in its server actions

## Summary
Severity: Medium
Advisory: GHSA-m2m6-cff5-3w7c
CVE: CVE-2026-42190
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-m2m6-cff5-3w7c
Type: github-advisory

## Affected
- npm: `rwsdk` — affected >=1.0.0-beta.50 <1.2.3

## Details
### Summary

Server actions in `rwsdk` apply HTTP method enforcement but no origin validation. A request originating from a different origin that the browser treats as same-site can invoke a server action with the victim's session cookie attached.

### Impact

An attacker who controls any origin the browser considers same-site with the deployed app can induce an authenticated victim's browser to invoke arbitrary server actions. The exposure depends on deployment shape:

- Apps deployed on custom domains (for example `app.example.com`) are exposed whenever the attacker controls any sibling subdomain under the same registrable domain. Plausible vectors include subdomain takeover of stale DNS records pointing at third-party services, cross-site scripting on a sibling application, or content served from a user-content subdomain.
- Apps deployed on platform-suffix domains on the Public Suffix List (`*.workers.dev`, `*.pages.dev`) are not exposed to the sibling-subdomain vector, because sibling subdomains under those suffixes are treated as cross-site.
- In local development, `localhost` on any other port is treated as same-site with the app's dev server. A separate process running on the developer's machine can invoke server actions against the dev server.

The attacker cannot read action responses (`mode: "no-cors"` yields opaque responses). Impact is therefore limited to side effects of action invocation: writes, state changes, and any externally observable action the application performs in response.

Cross-site requests from unrelated origins (`evil.com` targeting `app.com`) are not affected because `SameSite=Lax` session cookies are not attached by default in that scenario.

### Affected Configurations

Applications using `rwsdk` server actions (`serverAction()` or functions invoked via the RSC action protocol) in combination with cookie-based authentication. `serverQuery()` is not affected because it is designed to be idempotent and is invoked via GET.

### Patch

The patched release enforces an Origin/Host match for non-GET action requests. Requests whose `Origin` header does not match the request's own origin are rejected with HTTP 403 unless the origin is listed in a new `allowedOrigins` configuration option.

No application code changes are required for apps that invoke server actions from their own origin. Apps that legitimately invoke server actions from another origin must add those origins to the `allowedOrigins` option on `defineApp`.

### Credits

Reported by `@mthx`.

## References
- https://github.com/redwoodjs/sdk/security/advisories/GHSA-m2m6-cff5-3w7c
- https://nvd.nist.gov/vuln/detail/CVE-2026-42190
- https://github.com/redwoodjs/sdk
- https://github.com/redwoodjs/sdk/releases/tag/v1.2.3
