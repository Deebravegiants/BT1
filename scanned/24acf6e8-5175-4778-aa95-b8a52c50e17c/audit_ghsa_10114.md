# [M] OpenTelemetry dotnet: Excessive memory allocation when parsing OpenTelemetry propagation headers

## Summary
Severity: Medium
Advisory: GHSA-g94r-2vxg-569j
CVE: CVE-2026-40894
CWE: CWE-789
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-04-23
Source: https://github.com/advisories/GHSA-g94r-2vxg-569j
Type: github-advisory

## Affected
- NuGet: `OpenTelemetry.Api` — affected >=0.5.0-beta.2 <1.15.3
- NuGet: `OpenTelemetry.Extensions.Propagators` — affected >=1.3.1 <1.15.3

## Details
### Summary

The implementation details of the baggage, B3 and Jaeger processing code in the `OpenTelemetry.Api` and `OpenTelemetry.Extensions.Propagators` NuGet packages can allocate excessive memory when parsing which could create a potential denial of service (DoS) in the consuming application.

### Details

#### Exceeding Limits

[`BaggagePropagator.Inject<T>()`](https://github.com/open-telemetry/opentelemetry-dotnet/blob/fc1a2864d1665bda857089e11fe9247e3c75637a/src/OpenTelemetry.Api/Context/Propagation/BaggagePropagator.cs#L93-L112) does not enforce the length limit of `8192` characters if the injected baggage contains only one item.

This change was introduced by #1048.

#### Excessive allocation

The following methods eagerly allocate intermediate arrays before applying size limits.

- [`BaggagePropagator.Extract<T>()`](https://github.com/open-telemetry/opentelemetry-dotnet/blob/888d1bf2489fb7408d3c5e8758a5bbffa89a8fb2/src/OpenTelemetry.Api/Context/Propagation/BaggagePropagator.cs#L52-L55) - this change was introduced by #1048.
- [`BaggagePropagator.Inject<T>()`](https://github.com/open-telemetry/opentelemetry-dotnet/blob/888d1bf2489fb7408d3c5e8758a5bbffa89a8fb2/src/OpenTelemetry.Api/Context/Propagation/BaggagePropagator.cs#L138-L157) - this change was introduced by #1048.
- [`B3Propagator.Extract<T>()`](https://github.com/open-telemetry/opentelemetry-dotnet/blob/888d1bf2489fb7408d3c5e8758a5bbffa89a8fb2/src/OpenTelemetry.Extensions.Propagators/B3Propagator.cs#L203-L207) - this change was introduced by #533.
- [`B3Propagator.Extract<T>()`](https://github.com/open-telemetry/opentelemetry-dotnet/blob/888d1bf2489fb7408d3c5e8758a5bbffa89a8fb2/src/OpenTelemetry.Api/Context/Propagation/B3Propagator.cs#L204-L214) - this change was introduced by #3244.
- [`JaegerPropagator.Extract<T>()`](https://github.com/open-telemetry/opentelemetry-dotnet/blob/888d1bf2489fb7408d3c5e8758a5bbffa89a8fb2/src/OpenTelemetry.Extensions.Propagators/JaegerPropagator.cs#L150-L154) - this change was introduced by #3309.

### Impact

Excessively large propagation headers, particularly in degenerate/malformed cases that consist or large numbers of delimiter characters, can allocate excessive amounts of memory for intermediate storage of parsed content relative to the size of the original input.

### Mitigation

HTTP servers often set maximum limits on the length of HTTP request headers, such as [Internet Information Services (IIS)](https://learn.microsoft.com/iis/configuration/system.webserver/security/requestfiltering/requestlimits/headerlimits/) which sets a default limit of 16KB and [nginx](https://nginx.org/docs/http/ngx_http_core_module.html#large_client_header_buffers) which sets a default limit of 8KB.

### Workarounds

Possible workarounds include:

- Configuring appropriate HTTP request header limits.
- Disabling baggage and/or trace propagation.

### Remediation

[#7061](https://github.com/open-telemetry/opentelemetry-dotnet/pull/7061) refactors the handling of baggage, B3 and Jaeger propagation headers to stop parsing eagerly when limits are exceeded and avoid allocating intermediate arrays.

## References
- https://github.com/open-telemetry/opentelemetry-dotnet/security/advisories/GHSA-g94r-2vxg-569j
- https://nvd.nist.gov/vuln/detail/CVE-2026-40894
- https://github.com/open-telemetry/opentelemetry-dotnet/pull/1048
- https://github.com/open-telemetry/opentelemetry-dotnet/pull/3244
- https://github.com/open-telemetry/opentelemetry-dotnet/pull/3309
- https://github.com/open-telemetry/opentelemetry-dotnet/pull/3533
- https://github.com/open-telemetry/opentelemetry-dotnet/pull/533
- https://github.com/open-telemetry/opentelemetry-dotnet/pull/7061
- https://github.com/open-telemetry/opentelemetry-dotnet
- https://github.com/open-telemetry/opentelemetry-dotnet/releases/tag/core-1.15.3
