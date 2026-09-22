# [M] Swift W3C TraceContext vulnerable to a malformed HTTP header causing a crash

## Summary
Severity: Medium
Advisory: GHSA-mvpq-2v8x-ww6g
CVE: CVE-2026-23886
CWE: CWE-20
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-mvpq-2v8x-ww6g
Type: github-advisory

## Affected
- SwiftURL: `github.com/swift-otel/swift-w3c-trace-context` — affected >=0 <1.0.0-beta.5
- SwiftURL: `github.com/swift-otel/swift-otel` — affected >=0 <1.0.4

## Details
### Impact

A denial-of-service vulnerability due to improper input validation allows a remote attacker to crash the service via a malformed HTTP header.

Allows crashing the process with data coming from the network when used with, for example, an HTTP server. Most common way of using Swift W3C Trace Context is through Swift OTel.

### Patches

https://github.com/swift-otel/swift-w3c-trace-context/commit/5da9b143ba6046734de3fa51dafea28290174e4e

### Workarounds
Disable either Swift OTel or the code that extracts the trace information from an incoming header (such as a `TracingMiddleware`).

### References

[Swift W3C TraceContext 1.0.0-beta.5](https://github.com/swift-otel/swift-w3c-trace-context/releases/tag/1.0.0-beta.5)
[Swift OTel 1.0.4](https://github.com/swift-otel/swift-otel/releases/tag/1.0.4)

## References
- https://github.com/swift-otel/swift-w3c-trace-context/security/advisories/GHSA-mvpq-2v8x-ww6g
- https://nvd.nist.gov/vuln/detail/CVE-2026-23886
- https://github.com/swift-otel/swift-w3c-trace-context/commit/5da9b143ba6046734de3fa51dafea28290174e4e
- https://github.com/swift-otel/swift-otel/releases/tag/1.0.4
- https://github.com/swift-otel/swift-w3c-trace-context
- https://github.com/swift-otel/swift-w3c-trace-context/releases/tag/1.0.0-beta.5
