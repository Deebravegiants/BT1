# [H] @fastify/oauth2 vulnerable to Cross Site Request Forgery due to reused Oauth2 state

## Summary
Severity: High
Advisory: GHSA-g8x5-p9qc-cf95
CVE: CVE-2023-31999
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-05
Source: https://github.com/advisories/GHSA-g8x5-p9qc-cf95
Type: github-advisory

## Affected
- npm: `@fastify/oauth2` — affected >=0 <7.2.0

## Details
### Impact

All versions of @fastify/oauth2 used a statically generated `state` parameter at startup time and were used across all requests for all users.
The purpose of the Oauth2 `state` parameter is to prevent Cross-Site-Request-Forgery attacks. As such, it should be unique per user and should be connected to the user's session in some way that will allow the server to validate it.

### Patches

v7.2.0 changes the default behavior to store the `state` in a cookie with the `http-only` and `same-site=lax` attributes set. The state is now by default generated for every user.

Note that this contains a breaking change in the `checkStateFunction` function, which now accepts the full `Request` object.

### Workarounds

There are no known workarounds.

### References

* [Prevent Attacks and Redirect Users with OAuth 2.0 State Parameters](https://auth0.com/docs/secure/attack-protection/state-parameters)

## References
- https://github.com/fastify/fastify-oauth2/security/advisories/GHSA-g8x5-p9qc-cf95
- https://nvd.nist.gov/vuln/detail/CVE-2023-35935
- https://github.com/fastify/fastify-oauth2/commit/bff756b456cbb769080631af2beb85671ff4c79c
- https://auth0.com/docs/secure/attack-protection/state-parameters
- https://github.com/fastify/fastify-oauth2
- https://github.com/fastify/fastify-oauth2/releases/tag/v7.2.0
