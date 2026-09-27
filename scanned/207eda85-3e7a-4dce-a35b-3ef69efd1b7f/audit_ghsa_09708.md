# [M] OpenTelemetry's disk retry default temp path enables local blob injection via OTLP Exporter

## Summary
Severity: Medium
Advisory: GHSA-4625-4j76-fww9
CVE: CVE-2026-42191
CWE: CWE-379
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-04-30
Source: https://github.com/advisories/GHSA-4625-4j76-fww9
Type: github-advisory

## Affected
- NuGet: `OpenTelemetry.Exporter.OpenTelemetryProtocol` — affected >=1.8.0 <1.15.3

## Details
### Summary

The OTLP disk retry feature in `OpenTelemetry.Exporter.OpenTelemetryProtocol` silently fell back to `Path.GetTempPath()` when `OTEL_DOTNET_EXPERIMENTAL_OTLP_RETRY=disk` was set but `OTEL_DOTNET_EXPERIMENTAL_OTLP_DISK_RETRY_DIRECTORY_PATH` was not configured.

The exporter stored and loaded `*.blob` files under fixed, signal-named subdirectories (`traces`, `metrics`, `logs`) beneath that shared temporary root path.

On multi-user systems where the temporary directory is accessible to other local accounts, this exposed three attack surfaces:

- **Blob injection (integrity):** an attacker could write crafted `*.blob` files into the predictable path; the exporter picks them up on the next retry cycle and forwards them to the configured OTLP endpoint under the application's identity.
- **Telemetry disclosure (confidentiality):** an attacker reads `*.blob` files written by the application between export failures, recovering encoded telemetry payloads (spans, metric data points, log records).
- **Resource exhaustion (availability):** an attacker deposits numerous or oversized blob files, degrading retry-loop performance or consuming disk space.

### Details

#### Preconditions

1. `OTEL_DOTNET_EXPERIMENTAL_OTLP_RETRY` is set to `disk`.
2. `OTEL_DOTNET_EXPERIMENTAL_OTLP_DISK_RETRY_DIRECTORY_PATH` is not set, causing the exporter to resolve the blob storage root using the `System.IO.Path.GetTempPath()` API.
3. A local attacker has read or write access to the process' temporary directory (e.g., `/tmp` on Linux, or `%TEMP%` on a multi-user Windows installation).

#### Exploit path

1. A target application starts with `OTEL_DOTNET_EXPERIMENTAL_OTLP_RETRY=disk` and no explicit blob directory. The exporter resolves the storage root to `Path.GetTempPath()`, producing paths such as `%TEMP%\traces`, `%TEMP%\metrics`, and `%TEMP%\logs` (or `/tmp/traces` etc. on Linux).
2. **Injection scenario:** before or during the application's retry window, an attacker writes crafted `*.blob` files into one of those signal subdirectories. On the next retry interval (by default every 60 seconds), [`OtlpExporterPersistentStorageTransmissionHandler`](https://github.com/open-telemetry/opentelemetry-dotnet/blob/c724f4bd6fd88e9a599af1668bf7af9487155b62/src/OpenTelemetry.Exporter.OpenTelemetryProtocol/Implementation/Transmission/OtlpExporterPersistentStorageTransmissionHandler.cs) scans the directory, loads the attacker-supplied blobs, and forwards them to the configured OTLP endpoint using the application's identity and transport credentials.
3. **Disclosure scenario:** the attacker reads `*.blob` files that the application wrote after a transient export failure, recovering the full serialized telemetry payloads (spans, metric data points, or log records in Protobuf encoding).
5. **DoS scenario:** the attacker deposits a large number of oversized blob files in the temporary subdirectories, causing the retry loop to consume excess CPU/IO processing them, potentially exhausting available disk space.

### Mitigations

If an immediate upgrade to a patched version is not possible:

1. Avoid enabling disk retry in shared environments.
2. Configure a dedicated directory with strict ACL/ownership and least privilege.
3. Ensure the directory is not shared across tenants/users.
4. Monitor for unexpected `*.blob` files or abnormal retry backlog growth.

### Resources

- [#7106](https://github.com/open-telemetry/opentelemetry-dotnet/pull/7106)

## References
- https://github.com/open-telemetry/opentelemetry-dotnet/security/advisories/GHSA-4625-4j76-fww9
- https://nvd.nist.gov/vuln/detail/CVE-2026-42191
- https://github.com/open-telemetry/opentelemetry-dotnet/pull/7106
- https://github.com/open-telemetry/opentelemetry-dotnet/commit/78dffdc5ebdf3dc090fdb94e3f1a32d3d1e26dfd
- https://github.com/open-telemetry/opentelemetry-dotnet
