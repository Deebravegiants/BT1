# [M] OpenTelemetry .NET has Denial of Service (DoS) Vulnerability in API Package

## Summary
Severity: Medium
Advisory: GHSA-8785-wc3w-h8q6
CVE: CVE-2025-27513
CWE: CWE-770
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-05
Source: https://github.com/advisories/GHSA-8785-wc3w-h8q6
Type: github-advisory

## Affected
- NuGet: `OpenTelemetry.Api` — affected >=1.11.0 <1.11.2
- NuGet: `OpenTelemetry.Api` — affected 1.10.0
- NuGet: `OpenTelemetry.Api` — affected 1.10.0-beta.1
- NuGet: `OpenTelemetry.Api` — affected 1.10.0-rc.1
- NuGet: `OpenTelemetry.Api` — affected 1.11.0-rc.1

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

A vulnerability in `OpenTelemetry.Api` package `1.10.0` to `1.11.1` could cause a Denial of Service (DoS) when a `tracestate` and `traceparent` header is received.

* Even if an application does not explicitly use trace context propagation, receiving these headers can still trigger high CPU usage.
* This issue impacts any application accessible over the web or backend services that process HTTP requests containing a `tracestate` header.
* Application may experience excessive resource consumption, leading to increased latency, degraded performance, or downtime.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

This issue has been <strong data-start="1143" data-end="1184">resolved in OpenTelemetry.Api 1.11.2</strong> by <strong data-start="1188" data-end="1212">reverting the change</strong> that introduced the problematic behavior in versions <strong data-start="1266" data-end="1286">1.10.0 to 1.11.1</strong>.</li><li data-start="1290" data-end="1409">The fix ensures that <strong data-start="1313" data-end="1380">valid tracing headers no longer cause excessive CPU consumption</strong> when received in requests.</li></ul><h4 data-start="1411" data-end="1434"><strong data-start="1416" data-end="1434">Fixed Version:</strong></h4>
OpenTelemetry .NET Version | Status
-- | --
<= 1.9.x | ✅ Not affected
1.10.0 - 1.11.1 | ❌ Vulnerable
1.11.2 (Fixed) | ✅ Safe to use

**Upgrade Command:**

```
dotnet add package OpenTelemetry --version 1.11.2
```

**Delisting of Affected Packages**
To prevent accidental usage, we have delisted the affected versions (1.10.0 to 1.11.1) from NuGet. Users should avoid these versions and upgrade to 1.11.2 immediately.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/open-telemetry/opentelemetry-dotnet/security/advisories/GHSA-8785-wc3w-h8q6
- https://nvd.nist.gov/vuln/detail/CVE-2025-27513
- https://github.com/open-telemetry/opentelemetry-dotnet/pull/6161
- https://github.com/open-telemetry/opentelemetry-dotnet/commit/1b555c1201413f2f55f2cd3c4ba03ef4b615b6b5
- https://github.com/open-telemetry/opentelemetry-dotnet
