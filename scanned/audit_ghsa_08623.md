# [M] OpenTelemetry.Exporter.Instana bypasses TLS certificate validation when a proxy is configured

## Summary
Severity: Medium
Advisory: GHSA-wfr5-454p-mjc2
CVE: CVE-2026-44213
CWE: CWE-295
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-wfr5-454p-mjc2
Type: github-advisory

## Affected
- NuGet: `OpenTelemetry.Exporter.Instana` — affected >=0 <1.1.0

## Details
### Summary

The `OpenTelemetry.Exporter.Instana` NuGet package does not validate HTTPS/TLS certificates are valid when sending telemetry to a configured Instana back-end when a proxy is configured using the `INSTANA_ENDPOINT_PROXY` environment variable.

If a network attacker can Man-in-the-Middle (MitM) the proxy connection, all OpenTelemetry telemetry data and the Instana API key are exposed to the attacker.

### Details

The [`Transport.ConfigureBackendClient()`](https://github.com/open-telemetry/opentelemetry-dotnet-contrib/blob/b53b6a74fde21a4cee344e584b51a0fe5bf1f337/src/OpenTelemetry.Exporter.Instana/Implementation/Transport.cs#L132-L158) method creates an `HttpClient` instance that completely disables TLS server certificate validation if the `INSTANA_ENDPOINT_PROXY` is configured with a valid proxy URL with no ability to re-enable it.

### Impact

If the configured proxy is attacker-controlled (or a network attacker MitM the connection), or if it is possible for the process' configuration to be changed to add an attacker-provided value for `INSTANA_ENDPOINT_PROXY` then all Instana telemetry could be read by an unauthorized party and the service's Instana API key compromised, potentially before being forwarded to Instana presenting no noticeable loss of telemetry data without a valid TLS server certificate being presented to the client that matches the expected hostname or IP address.

### Mitigation

The proxy configured by the `INSTANA_ENDPOINT_PROXY` environment variable must be malicious or be possible to be subject to a MitM attack.

### Workarounds

Do not configure the `INSTANA_ENDPOINT_PROXY` environment variable.

### Remediation

[#4153](https://github.com/open-telemetry/opentelemetry-dotnet-contrib/pull/4153) refactors `HttpClient` creation so that TLS certificate validation is no longer disabled by default when using a proxy.

In environments where this capability is required, for example for local development, the previous behaviour can be restored using the `` option:

```csharp
builder.AddInstanaExporter((options) =>
{
    options.HttpClientFactory = () =>
    {
        var handler = new HttpClientHandler()
        {
#if NET
            ServerCertificateCustomValidationCallback = HttpClientHandler.DangerousAcceptAnyServerCertificateValidator,
#else
            ServerCertificateCustomValidationCallback = static (_, _, _, _) => true,
#endif
        };
        return new HttpClient(handler, disposeHandler: true);
    };
});
```

### Resources

- [PR #4153](https://github.com/open-telemetry/opentelemetry-dotnet-contrib/pull/4153)

## References
- https://github.com/open-telemetry/opentelemetry-dotnet-contrib/security/advisories/GHSA-wfr5-454p-mjc2
- https://nvd.nist.gov/vuln/detail/CVE-2026-44213
- https://github.com/open-telemetry/opentelemetry-dotnet-contrib
