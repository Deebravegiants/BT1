# [M] OpenTelemetry dotnet: Unbounded `grpc-status-details-bin` parsing in OTLP/gRPC retry handling

## Summary
Severity: Medium
Advisory: GHSA-mr8r-92fq-pj8p
CVE: CVE-2026-40891
CWE: CWE-789
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-23
Source: https://github.com/advisories/GHSA-mr8r-92fq-pj8p
Type: github-advisory

## Affected
- NuGet: `OpenTelemetry.Exporter.OpenTelemetryProtocol` — affected >=1.13.1 <1.15.3

## Details
### Summary

When exporting telemetry over gRPC using the OpenTelemetry Protocol (OTLP), the exporter may parse a server-provided `grpc-status-details-bin` trailer during retry handling. Prior to the fix, a malformed trailer could encode an extremely large length-delimited protobuf field which was used directly for allocation, allowing excessive memory allocation and potential denial of service (DoS).

### Details

#5980 introduced a retry path that parses `grpc-status-details-bin` to extract gRPC retry delay information for retryable responses.

On that path:

- `OtlpGrpcExportClient` captures `grpc-status-details-bin` from retryable status responses (`ResourceExhausted` / `Unavailable`).
- `OtlpRetry` invokes `GrpcStatusDeserializer.TryGetGrpcRetryDelay` using this untrusted trailer value.
- `GrpcStatusDeserializer.DecodeBytes` decoded a protobuf varint length and allocated `new byte[length]` without validating the bounds against the remaining payload size.

A malicious or compromised collector (or a MitM in weakly-protected deployments) could return a crafted `grpc-status-details-bin` payload that forces oversized allocation and memory exhaustion in the instrumented process.

### Impact

If an OTLP/gRPC endpoint is attacker-controlled (or traffic is intercepted), a crafted retryable response can trigger large allocations during trailer parsing, which may exhaust memory and cause process instability/crash (availability impact / DoS).

### Mitigation

The application's configured back-end/collector endpoint needs to behave maliciously. If the collector/back-end is a well-behaved implementation response bodies should not be excessively large if a request error occurs.

### Workarounds

None known.

### Remediation

[#7064](https://github.com/open-telemetry/opentelemetry-dotnet/pull/7064) updates `GrpcStatusDeserializer` to validate decoded length-delimited field sizes before allocation by ensuring the requested length is sane and does not exceed the remaining payload.

This causes malformed or truncated `grpc-status-details-bin` payloads to fail safely instead of attempting unbounded allocation.

## References
- https://github.com/open-telemetry/opentelemetry-dotnet/security/advisories/GHSA-mr8r-92fq-pj8p
- https://nvd.nist.gov/vuln/detail/CVE-2026-40891
- https://github.com/open-telemetry/opentelemetry-dotnet/pull/5980
- https://github.com/open-telemetry/opentelemetry-dotnet/pull/7064
- https://github.com/open-telemetry/opentelemetry-dotnet
