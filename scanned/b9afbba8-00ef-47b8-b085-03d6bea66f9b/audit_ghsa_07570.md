# [H] Apollo Serve vulnerable to Denial of Service with `startStandaloneServer`

## Summary
Severity: High
Advisory: GHSA-mp6q-xf9x-fwf7
CVE: CVE-2026-23897
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-mp6q-xf9x-fwf7
Type: github-advisory

## Affected
- npm: `apollo-server` — affected >=2.0.0
- npm: `@apollo/server` — affected >=4.2.0 <4.13.0
- npm: `@apollo/server` — affected >=5.0.0 <5.4.0

## Details
### Impact

The default configuration of `startStandaloneServer` from `@apollo/server/standalone` is vulnerable to Denial of Service (DoS) attacks through specially crafted request bodies with exotic character set encodings.

This issue does not affect users that use `@apollo/server` as a dependency for integration packages, like `@as integrations/express5` or `@as-integrations/next`, only direct usage of `startStandaloneServer`.

### Who is impacted

Users directly using `startStandaloneServer` from `@apollo/server/standalone`.

This issue affects Apollo Server from v5.0.0 through v5.3.x.

It also affects all releases of the end-of-life major versions v4, v3, and v2.  Although Apollo Server v4 is EOL and Apollo no longer commits to providing support or updates for it, a fix for it was released in v4.13.0.  Apollo Server v3 and v2 are no longer updated, as they have been EOL since 2024 and 2023 respectively.

### Patches

Patches for this issue are released as `@apollo/server` versions `5.4.0` and `4.13.0`.

In accordance with [RFC 7159](https://datatracker.ietf.org/doc/html/rfc7159#section-8.1), these versions now only accept request bodies encoded in UTF-8, UTF-16 (LE or BE), or UTF-32 (LE or BE). Any other character set will be rejected with a `415 Unsupported Media Type` error. Note that the more recent JSON RFC, [RFC 8259 (https://datatracker.ietf.org/doc/html/rfc8259#section-8.1), is more strict and will only allow UTF-8. Since this is a minor release, we have chosen to remain compatible with the more permissive RFC 7159 for now. In a future major release, the restriction may be tightened further to only allow UTF-8.

### Workarounds

Users of `apollo-server` v2 or v3 that cannot upgrade for some reason could switch from the standalone `apollo-server`
package to an integration package like `apollo-server-express` or `apollo-server-koa` and set up their own server. Please note that these old packages are generally EOL and do not receive any more support or bug fixes. This can only be seen as a short-term workaround. Updating to `@apollo/server` v5 should be a priority.

## References
- https://github.com/apollographql/apollo-server/security/advisories/GHSA-mp6q-xf9x-fwf7
- https://nvd.nist.gov/vuln/detail/CVE-2026-23897
- https://github.com/apollographql/apollo-server/commit/d25a5bdc377826ad424fcf7f8d1d062055911643
- https://github.com/apollographql/apollo-server/commit/e9d49d163a86b8a33be56ed27c494b9acd5400a4
- https://github.com/apollographql/apollo-server
