# [M] Sensitive query parameters logged by default in OpenTelemetry.Instrumentation http and AspNetCore

## Summary
Severity: Medium
Advisory: GHSA-vh2m-22xx-q94f
CVE: CVE-2024-32028
CWE: CWE-201, CWE-212
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-04-12
Source: https://github.com/advisories/GHSA-vh2m-22xx-q94f
Type: github-advisory

## Affected
- NuGet: `OpenTelemetry.Instrumentation.Http` — affected >=0 <1.8.1
- NuGet: `OpenTelemetry.Instrumentation.AspNetCore` — affected >=0 <1.8.1

## Details
## Impact

`OpenTelemetry.Instrumentation.Http` writes the `url.full` attribute/tag on spans (`Activity`) when tracing is enabled for outgoing http requests and `OpenTelemetry.Instrumentation.AspNetCore` writes the `url.query` attribute/tag on spans (`Activity`) when tracing is enabled for incoming http requests.

These attributes are defined by the [Semantic Conventions for HTTP Spans](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/http/http-spans.md).

Up until the `1.8.1` the values written by `OpenTelemetry.Instrumentation.Http` & `OpenTelemetry.Instrumentation.AspNetCore` will pass-through the raw query string as was sent or received (respectively). This may lead to sensitive information (e.g. EUII - End User Identifiable Information, credentials, etc.) being leaked into telemetry backends (depending on the application(s) being instrumented) which could cause privacy and/or security incidents.

Note: Older versions of `OpenTelemetry.Instrumentation.Http` & `OpenTelemetry.Instrumentation.AspNetCore` may use different tag names but have the same vulnerability.

## Resolution

The `1.8.1` versions of `OpenTelemetry.Instrumentation.Http` & `OpenTelemetry.Instrumentation.AspNetCore` will now redact by default all values detected on transmitted or received query strings.

Example transmitted or received query sting:

`?key1=value1&key2=value2`

Example of redacted value written on telemetry:

`?key1=Redacted&key2=Redacted`

## References
- https://github.com/open-telemetry/opentelemetry-dotnet/security/advisories/GHSA-vh2m-22xx-q94f
- https://nvd.nist.gov/vuln/detail/CVE-2024-32028
- https://github.com/open-telemetry/opentelemetry-dotnet/commit/e222ecb5942d4ce1cadfd4306c39e3f4933a5c42
- https://github.com/open-telemetry/opentelemetry-dotnet
- https://github.com/open-telemetry/semantic-conventions/blob/main/docs/http/http-spans.md
