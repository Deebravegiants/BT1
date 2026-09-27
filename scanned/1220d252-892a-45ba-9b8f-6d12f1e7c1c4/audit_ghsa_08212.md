# [M] Vert.x has a DoS via unbounded server-side SNI SslContext cache growth

## Summary
Severity: Medium
Advisory: GHSA-3g76-f9xq-8vp6
CVE: CVE-2026-6860
CWE: CWE-295, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-09
Source: https://github.com/advisories/GHSA-3g76-f9xq-8vp6
Type: github-advisory

## Affected
- Maven: `io.vertx:vertx-core` — affected >=4.3.4
- Maven: `io.vertx:vertx-core` — affected >=4.4.0
- Maven: `io.vertx:vertx-core` — affected >=4.5.0 <4.5.27
- Maven: `io.vertx:vertx-core` — affected >=5.0.0 <5.0.12

## Details
Potential unbounded server-side SNI `SslContext` cache growth in Vert.x TLS handling, with = resource-exhaustion / DoS impact. On affected versions, matching server-side SNI names are cached via `computeIfAbsent(serverName, ...)` in a serverName-keyed `SslContext` cache.

The implementation differs slightly by branch, but the same sink appears to be present in released versions `4.3.4` through `5.0.11`:
- `4.3.x`: `SSLHelper`
- `4.4.x` / `4.5.x`: `SslChannelProvider`
- `5.0.x` and current `master`: `SslContextProvider`

When server-side SNI is enabled and wildcard or otherwise broad hostname mappings are used, an unauthenticated client can send many distinct matching SNI names and cause the server to retain increasing numbers of `SslContext` entries over time, leading to increasing memory consumption and possible DoS conditions.

## Steps to reproduce

1. Configure a Vert.x server with `setSsl(true)` and `setSni(true)`.
2. Use a keystore or mapping where many distinct SNI names match a wildcard or similarly broad rule.
3. Send repeated connections with distinct matching SNI values.
4. Observe that the SNI cache size grows with the number of unique matching names.

## What are the affected versions?

Affected released versions confirmed on `origin`:
- `4.3.4` through `4.3.8`
- `4.4.0` through `4.4.9`
- `4.5.0` through `4.5.26`
- `5.0.0` through `5.0.11`

Not affected by the same sink:
- `4.0.x` through `4.2.x`
- `4.3.0` through `4.3.3`

## References
- https://github.com/eclipse-vertx/vert.x/security/advisories/GHSA-3g76-f9xq-8vp6
- https://nvd.nist.gov/vuln/detail/CVE-2026-6860
- https://github.com/eclipse-vertx/vert.x/pull/6102
- https://github.com/eclipse-vertx/vert.x
- https://github.com/vert-x3/wiki/wiki/4.5.27-Release-Notes
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/381
- https://vertx.io/blog/eclipse-vert-x-4-5-27
- https://vertx.io/blog/eclipse-vert-x-5-0-12
