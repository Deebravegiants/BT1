# [H] Cached redirect poisoning via X-Forwarded-Host header

## Summary
Severity: High
Advisory: GHSA-w6rq-6h34-vh7q
CVE: CVE-2021-29479
CWE: CWE-807
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2021-07-01
Source: https://github.com/advisories/GHSA-w6rq-6h34-vh7q
Type: github-advisory

## Affected
- Maven: `io.ratpack:ratpack-core` — affected >=0 <1.9.0

## Details
A user supplied `X-Forwarded-Host` header can be used to perform cache poisoning of a cache fronting a Ratpack server if the cache key does not include the `X-Forwarded-Host` header as a cache key.

Users are only vulnerable if they do not configure a custom `PublicAddress` instance. A custom `PublicAddress` can be specified by using [ServerConfigBuilder::publicAddress](https://ratpack.io/manual/current/api/ratpack/server/ServerConfigBuilder.html#publicAddress-java.net.URI-). For versions prior to 1.9.0, by default, Ratpack utilizes an inferring version of `PublicAddress` which is vulnerable.

### Impact

This can be used to perform redirect cache poisoning where an attacker can force a cached redirect to redirect to their site instead of the intended redirect location.

### Patches

As of Ratpack 1.9.0, two changes have been made that mitigate this vulnerability:

1. The default PublicAddress implementation no longer infers the address from the request context, instead relying on the configured bind host/port
2. Relative redirects issued by the application are no longer absolutized; they are passed through as-is

### Workarounds

In production, ensure that [ServerConfigBuilder::publicAddress](https://ratpack.io/manual/current/api/ratpack/server/ServerConfigBuilder.html#publicAddress-java.net.URI-) correctly configures the server.

### References
 - https://portswigger.net/web-security/web-cache-poisoning

## References
- https://github.com/ratpack/ratpack/security/advisories/GHSA-w6rq-6h34-vh7q
- https://nvd.nist.gov/vuln/detail/CVE-2021-29479
- https://github.com/ratpack/ratpack
- https://portswigger.net/web-security/web-cache-poisoning
