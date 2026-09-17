# [M] Netty: Security Control Bypass via CORS Short-Circuit Failure

## Summary
Severity: Medium
Advisory: GHSA-6cqp-g7gg-8hr5
CVE: CVE-2026-56746
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-6cqp-g7gg-8hr5
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http` — affected >=4.2.0.Final <4.2.16.Final
- Maven: `io.netty:netty-codec-http` — affected >=0 <4.1.136.Final

## Details
### Summary
Netty's CorsHandler provides a `shortCircuit()` configuration designed to reject unauthorized cross-origin requests immediately, acting as a security control before requests reach the application. However, due to a logical operator error in the origin evaluation process, this protection can be entirely bypassed. An attacker can bypass the short-circuit mechanism by sending a request with an `Origin: null` header. This failure forwards unauthorized requests to the backend application, bypassing intended access controls.

### Details
In `io.netty.handler.codec.http.cors.CorsHandler#channelRead`, the short-circuit logic relies on the configuration returned by `getForOrigin(origin)` to determine if an origin is authorized. If `getForOrigin` returns a configuration object, the short-circuit check `(!(origin == null || config != null))` is bypassed, and the request proceeds to the backend.

The vulnerability is located in the `getForOrigin` method:

```java
            if (corsConfig.isNullOriginAllowed() || NULL_ORIGIN.equals(requestOrigin)) {
                return corsConfig;
            }
```

If an attacker sends `Origin: null`, `NULL_ORIGIN.equals(requestOrigin)` evaluates to true. The method returns the configuration object regardless of whether `isNullOriginAllowed()` was configured by the developer. The short-circuit is bypassed.

### Impact
Applications relying on CorsHandler's short-circuit feature to prevent unauthorized cross-origin requests from reaching their backend logic are completely exposed. The framework fails to enforce the developer's intended access controls, allowing unauthorized requests to be processed.

## References
- https://github.com/netty/netty/security/advisories/GHSA-6cqp-g7gg-8hr5
- https://nvd.nist.gov/vuln/detail/CVE-2026-56746
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.136.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.16.Final
