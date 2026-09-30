# [M] OpenTelemetry .NET has potential memory exhaustion via unbounded pooled-list sizing in Jaeger exporter conversion path

## Summary
Severity: Medium
Advisory: GHSA-38h3-2333-qx47
CVE: CVE-2026-41078
CWE: CWE-400, CWE-770
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-18
Source: https://github.com/advisories/GHSA-38h3-2333-qx47
Type: github-advisory

## Affected
- NuGet: `OpenTelemetry.Exporter.Jaeger` — affected >=0

## Details
### Summary

> [!IMPORTANT]  
> There is no plan to fix this issue as `OpenTelemetry.Exporter.Jaeger` was deprecated in 2023. It is for informational purposes only.

`OpenTelemetry.Exporter.Jaeger` may allow sustained memory pressure when the internal pooled-list sizing grows based on a large observed span/tag set and that enlarged size is reused for subsequent allocations. Under high-cardinality or attacker-influenced telemetry input, this can increase memory consumption and potentially cause denial of service.

### Details

The Jaeger exporter conversion path can append tag/event data into pooled list structures. In affected versions, pooled allocation sizing may be influenced by large observed payloads and reused globally across later allocations, resulting in persistent oversized rentals and elevated memory pressure. In environments where telemetry attributes/events can be influenced by untrusted input and limits are increased from defaults, this may lead to process instability or denial of service.

### Impact

Availability impact only. Confidentiality and integrity impacts are not expected.

### Workarounds / Mitigations

* Prefer maintained exporters (for example OpenTelemetry Protocol format (OTLP)) instead of the Jaeger exporter.

## References
- https://github.com/open-telemetry/opentelemetry-dotnet/security/advisories/GHSA-38h3-2333-qx47
- https://nvd.nist.gov/vuln/detail/CVE-2026-41078
- https://github.com/open-telemetry/opentelemetry-dotnet
