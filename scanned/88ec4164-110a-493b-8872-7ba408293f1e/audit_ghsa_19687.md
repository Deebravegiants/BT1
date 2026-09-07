# [H] DoS Vulnerability in TraceContextPropagator.Extract - OpenTelemetry.Api

## Summary
Severity: High
Advisory: GHSA-vc29-vg52-6643
CWE: CWE-770
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-06
Source: https://github.com/advisories/GHSA-vc29-vg52-6643
Type: github-advisory

## Affected
- NuGet: `OpenTelemetry.AutoInstrumentation` — affected >=1.10.0-beta.1 <1.11.0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

A vulnerability in `OpenTelemetry.Api` package `1.10.0` to `1.11.1` could cause a [Denial of Service (DoS) when a tracestate and traceparent header is received](https://github.com/open-telemetry/opentelemetry-dotnet/security/advisories/GHSA-8785-wc3w-h8q6). These versions are used in OpenTelemetry .NET Automatic Instrumentation `1.10.0-beta.1` and `1.10.0`.

Even if an application does not explicitly use trace context propagation, receiving these headers can still trigger high CPU usage.
This issue impacts any application accessible over the web or backend services that process HTTP requests containing a tracestate header.
Application may experience excessive resource consumption, leading to increased latency, degraded performance, or downtime.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

This issue has been resolved in `OpenTelemetry.Api` `1.11.2` by reverting the change that introduced the problematic behavior in versions `1.10.0` to `1.11.1`. OpenTelemetry .NET Automatic Instrumentation fixes it in `1.11.0` release.

## Fixed version

| OpenTelemetry .NET Automatic Instrumentation | Status |
|----|----|
| <= 1.9.0 | ✅ Not affected |
| 1.10.0-beta.1, 1.10.0 | ❌ Vulnerable |
| 1.11.0 (Fixed)| ✅ Safe to use|

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/open-telemetry/opentelemetry-dotnet-instrumentation/security/advisories/GHSA-vc29-vg52-6643
- https://github.com/open-telemetry/opentelemetry-dotnet/security/advisories/GHSA-8785-wc3w-h8q6
- https://nvd.nist.gov/vuln/detail/CVE-2025-27513
- https://github.com/open-telemetry/opentelemetry-dotnet-instrumentation
