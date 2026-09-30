# [M] OneCollector exporter reads unbounded HTTP response bodies

## Summary
Severity: Medium
Advisory: GHSA-55m9-299j-53c7
CVE: CVE-2026-41484
CWE: CWE-770
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-55m9-299j-53c7
Type: github-advisory

## Affected
- NuGet: `OpenTelemetry.Exporter.OneCollector` — affected >=0 <1.15.1

## Details
### Summary

When exporting telemetry to a back-end/collector over HTTP using the OpenTelemetry.Exporter.OneCollector exporter, if the request results in a unsuccessful request (i.e. HTTP 4xx or 5xx), the response is read into memory with no upper-bound on the number of bytes consumed.

This could cause memory exhaustion in the consuming application if the configured back-end/collector endpoint is attacker-controlled (or a network attacker can MitM the connection) and an extremely large body is returned by the response.

### Details

The [`HttpJsonPostTransport`](https://github.com/open-telemetry/opentelemetry-dotnet-contrib/blob/171c6b81f88831641b56b470e6f92862e605013d/src/OpenTelemetry.Exporter.OneCollector/Internal/Transports/HttpJsonPostTransport.cs) class reads the response body when a non-200 HTTP status code is received when exporting telemetry to aid debugging by operators so that the error response is included in the logs emitted by the exporter.

An attacker who controls the configured endpoint, or who can intercept traffic to them (MiTM), can return an arbitrarily large response body. This causes unbounded heap allocation in the consuming process, leading to high transient memory pressure, garbage-collection stalls, or an OutOfMemoryException that terminates the process.

### Impact

If an application using the OneCollector exporter is configured to use a back-end/collector endpoint that is attacker-controlled (or a network attacker can MitM the connection) and an extremely large body is returned by the response the application could have its memory exhausted and create a denial-of-service condition.

### Mitigation

The application's configured back-end/collector endpoint needs to behave maliciously. If the collector/back-end is a well-behaved implementation response bodies should not be excessively large if a request error occurs.

### Workarounds

Use network-level controls (firewall rules, mTLS, service mesh) to prevent Man-in-the-Middle (MitM) attacks on the configured back-end/collector endpoint.

### Remediation

[#4117](https://github.com/open-telemetry/opentelemetry-dotnet-contrib/pull/4117) updates the OneCollector exporter to limit the number of bytes read from the response body in an error condition to 4MiB.

### Resources

- [#4117](https://github.com/open-telemetry/opentelemetry-dotnet-contrib/pull/4117)

## References
- https://github.com/open-telemetry/opentelemetry-dotnet-contrib/security/advisories/GHSA-55m9-299j-53c7
- https://nvd.nist.gov/vuln/detail/CVE-2026-41484
- https://github.com/open-telemetry/opentelemetry-dotnet-contrib/pull/4117
- https://github.com/open-telemetry/opentelemetry-dotnet-contrib/commit/77dc5d14fcdf6c6b3aeba5f8bba5dfded90495c9
- https://github.com/open-telemetry/opentelemetry-dotnet-contrib
