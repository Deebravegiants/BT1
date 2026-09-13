# [M] OpenTelemetry's Zipkin remote endpoint cache could grow without bounds and increase memory pressure

## Summary
Severity: Medium
Advisory: GHSA-88hf-wf7h-7w4m
CVE: CVE-2026-41310
CWE: CWE-400, CWE-770
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-88hf-wf7h-7w4m
Type: github-advisory

## Affected
- NuGet: `OpenTelemetry.Exporter.Zipkin` — affected >=0 <1.15.3

## Details
### Summary

The Zipkin exporter remote endpoint cache accepted unbounded key growth derived from span attributes. In high-cardinality scenarios, this could increase process memory usage over time and degrade availability.

### Details

- Introduce a bounded, thread-safe LRU cache for remote endpoints.
- Enforce fixed maximum size to prevent unbounded growth.

### Impact

- A process using Zipkin export for client/producer spans could experience avoidable memory growth under sustained unique remote endpoint values.

### Resources

[#7081](https://github.com/open-telemetry/opentelemetry-dotnet/pull/7081)

## References
- https://github.com/open-telemetry/opentelemetry-dotnet/security/advisories/GHSA-88hf-wf7h-7w4m
- https://nvd.nist.gov/vuln/detail/CVE-2026-41310
- https://github.com/open-telemetry/opentelemetry-dotnet/pull/7081
- https://github.com/open-telemetry/opentelemetry-dotnet/commit/c724f4bd6fd88e9a599af1668bf7af9487155b62
- https://github.com/open-telemetry/opentelemetry-dotnet
