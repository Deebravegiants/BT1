# [M] @hapi/wreck leaks sensitive `Proxy-Authorization` header across cross-hostname redirects

## Summary
Severity: Medium
Advisory: GHSA-vhjm-w67q-g75c
CVE: CVE-2026-44979
CWE: CWE-200, CWE-522
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-vhjm-w67q-g75c
Type: github-advisory

## Affected
- npm: `@hapi/wreck` — affected >=0 <18.1.1

## Details
### Impact
When `@hapi/wreck` follows a 3xx redirect to a different hostname, only the `Authorization` and `Cookie` headers are stripped. The standard credential header `Proxy-Authorization` is forwarded intact to the redirect target, potentially exposing forward-proxy credentials to a host outside the original trust boundary.

Redirect following is opt-in. The redirects option defaults to false (no redirections followed), so applications are only affected if they have explicitly set redirects to a positive integer on the request or via `Wreck.defaults({ redirects: ... })`.

### Patches
`@hapi/wreck` 18.1.1 extends the cross-hostname strip set to include `proxy-authorization`. Upgrade to 18.1.1 or later.

### Workarounds
If upgrading is not immediately possible:
- Leave redirects at its default (`false`) — applications that never enable redirect following are not affected.
- If redirects are required, set redirects: 0 when calling endpoints with sensitive headers, or strip Proxy-Authorization from the headers before issuing the request.
- Use the `beforeRedirect` hook to manually strip proxy-authorization (and any other sensitive application headers) when `redirectOptions` targets a different hostname than the original request.

### Resources
- Related: [CVE-2024-30260 / GHSA-3787-6prv-h9w3 ](https://github.com/nodejs/undici/security/advisories/GHSA-3787-6prv-h9w3)(undici)
- [RFC 7235 §4.4 — Proxy-Authorization](https://datatracker.ietf.org/doc/html/rfc7235#section-4.4)

## References
- https://github.com/hapijs/wreck/security/advisories/GHSA-vhjm-w67q-g75c
- https://github.com/nodejs/undici/security/advisories/GHSA-3787-6prv-h9w3
- https://github.com/hapijs/wreck/commit/a5b6fac9c684621c1d5733d10a0257697cfea373
- https://github.com/hapijs/wreck
