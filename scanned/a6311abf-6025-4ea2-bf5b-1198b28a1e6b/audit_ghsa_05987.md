# [H] datadog-opentelemetry has unbounded W3C tracestate parsing that may lead to DoS

## Summary
Severity: High
Advisory: GHSA-gpwf-4h98-v82q
CVE: CVE-2026-54788
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-gpwf-4h98-v82q
Type: github-advisory

## Affected
- crates.io: `datadog-opentelemetry` — affected >=0.1.0 <0.3.3

## Details
### Impact
Datadog tracing libraries that implement W3C Trace Context (`tracecontext`) propagation parse the incoming `tracestate` header without enforcing a size cap on the Datadog vendor entry (`dd=...`). The `dd=` value contains semicolon-separated `key:value` pairs, and the parser allocates a hash-map entry for each pair. A remote, unauthenticated attacker can send a `tracestate` header whose `dd=` member is arbitrarily large (or contains an arbitrarily large number of pairs), forcing unbounded CPU and memory consumption per request and enabling a remote Denial of Service. `tracecontext` extraction is enabled by default in affected tracers, so any internet-facing service instrumented with an affected version is exposed unless `tracecontext` has been explicitly removed from the propagation style configuration.

### Patches
This is resolved in version 0.3.3 and later of the `dd-trace-rs` library.

### Workarounds
If you cannot upgrade immediately:
1. Disable `tracecontext` extraction by setting `DD_TRACE_PROPAGATION_STYLE_EXTRACT` to a value that does not include `tracecontext` (for example, `datadog`).
2. Cap the maximum HTTP request header size at an upstream proxy or web server.

## References
- https://github.com/DataDog/dd-trace-rs/security/advisories/GHSA-gpwf-4h98-v82q
- https://github.com/DataDog/dd-trace-rs/pull/218
- https://github.com/DataDog/dd-trace-rs/commit/77c5d185c71d0ea8103da0e6cf4cd50677ffacd2
- https://github.com/DataDog/dd-trace-rs
- https://github.com/DataDog/dd-trace-rs/releases/tag/datadog-opentelemetry-v0.3.3
