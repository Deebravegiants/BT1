# [H] OpenTelemetry JavaScript: Denial of service in `JaegerPropagator` via unhandled exception on a malformed header

## Summary
Severity: High
Advisory: GHSA-45rx-2jwx-cxfr
CVE: CVE-2026-59892
CWE: CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-45rx-2jwx-cxfr
Type: github-advisory

## Affected
- npm: `@opentelemetry/propagator-jaeger` — affected >=0 <2.9.0

## Details
## Summary

`@opentelemetry/propagator-jaeger` decodes incoming HTTP header values with `decodeURIComponent()` without handling decode errors. A single request carrying a malformed percent-encoded value (for example a bare `%`) in an `uber-trace-id` or `uberctx-*` header throws an uncaught `URIError`, terminating any Node.js process that uses `JaegerPropagator` as its active propagator.


## Impact

**Denial of Service:** Any unauthenticated remote attacker who can send an HTTP request to a service that has `JaegerPropagator` registered as the global propagator (e.g. via `OTEL_PROPAGATORS=jaeger` or `propagation.setGlobalPropagator(new JaegerPropagator())`) can terminate the process with a single request. Confidentiality and integrity are not affected.

## Am I affected?

This issue affects only a specific, opt-in configuration. If you use OpenTelemetry's default propagators (W3C TraceContext and Baggage), you are **not** affected.          

You are affected only if you have registered `JaegerPropagator` as the active propagator. Check for:

- `@opentelemetry/propagator-jaeger` in your dependency tree, **and**
- `OTEL_PROPAGATORS` set to `jaeger` (Jaeger only), **or** a direct `propagation.setGlobalPropagator(new JaegerPropagator())` call in your code.

Note: if `JaegerPropagator` is combined with other propagators through a `CompositePropagator` (for example `OTEL_PROPAGATORS=jaeger,tracecontext`), the process does not terminate - the composite propagator catches the error - but affected requests silently fail to extract context. You should still upgrade.


## Patched versions

- `@opentelemetry/propagator-jaeger` 2.9.0

## Remediation

Update `@opentelemetry/propagator-jaeger` to 2.9.0 or later. The propagator now ignores header values it cannot decode instead of throwing.

**Interim mitigation (if you cannot update):** Trace-context headers should never be accepted unfiltered from untrusted callers. Until you can upgrade, strip or validate the `uber-trace-id` and `uberctx-*` headers on inbound requests at your edge - for example with a reverse proxy, API gateway, or load balancer (nginx, Envoy, etc.) - so that only trusted upstream services can set them.

## Details

`JaegerPropagator.extract()` calls `decodeURIComponent()` on raw header values at two unguarded call sites: the `uber-trace-id` trace header and each `uberctx-*` baggage value. `decodeURIComponent()` throws `URIError: URI malformed` on invalid percent-encoding. Because the HTTP instrumentation extracts context before its request-handler error wrapper, and a single configured propagator is not wrapped in a `CompositePropagator` (which would otherwise catch the error), the exception propagates as an `uncaughtException` and terminates the process.

## Proof of concept

Against a service using `JaegerPropagator`:

```bash
curl -H 'uberctx-user: %' http://target/
# or
curl -H 'uber-trace-id: %' http://target/
```

The Node.js process exits with `URIError: URI malformed` and subsequent requests are refused.

## References
- https://github.com/open-telemetry/opentelemetry-js/security/advisories/GHSA-45rx-2jwx-cxfr
- https://nvd.nist.gov/vuln/detail/CVE-2026-59892
- https://github.com/open-telemetry/opentelemetry-js/commit/b1c196d49d54caae59741cca0a9d57d101d7ea88
- https://github.com/open-telemetry/opentelemetry-js
- https://github.com/open-telemetry/opentelemetry-js/releases/tag/v2.9.0
