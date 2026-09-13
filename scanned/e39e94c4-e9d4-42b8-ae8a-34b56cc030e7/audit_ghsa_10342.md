# [M] OpenTelemetry.Resources.Azure has an unbounded HTTP response body read

## Summary
Severity: Medium
Advisory: GHSA-vc24-j8c5-2vw4
CVE: CVE-2026-41483
CWE: CWE-770
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-vc24-j8c5-2vw4
Type: github-advisory

## Affected
- NuGet: `OpenTelemetry.Resources.Azure` — affected >=0 <1.15.1-beta.1

## Details
### Summary

`OpenTelemetry.Resources.Azure` reads unbounded HTTP response bodies from the Azure VM remote instance metadata service endpoint into memory.

This would allow an attacker-controlled endpoint or one acting as a Man-in-the-Middle (MitM) to cause excessive memory allocation and possible process termination (via Out of Memory (OOM)).

### Details

The [`AzureVmMetaDataRequestor`](https://github.com/open-telemetry/opentelemetry-dotnet-contrib/blob/171c6b81f88831641b56b470e6f92862e605013d/src/OpenTelemetry.Resources.Azure/AzureVmMetaDataRequestor.cs) class makes HTTP requests to the relevant Azure VM instance metadata service (`http://169.254.169.254`) to obtain metadata about the running process and its infrastructure.

An attacker who controls the configured endpoint, or who can intercept traffic to them (MiTM), can return an arbitrarily large response body. This causes unbounded heap allocation in the consuming process, leading to high transient memory pressure, garbage-collection stalls, or an `OutOfMemoryException` that terminates the process.

### Impact

Denial of Service (DoS). An attacker can destabilize or crash the application by forcing unbounded memory allocation through the Azure VM instance metadata HTTP response paths.

### Mitigating Factors

The application's reachable Azure VM metadata endpoint needs to behave maliciously or be subject to MitM. In normal usage response bodies should not be excessively large.

### Patches

Fixed in `OpenTelemetry.Resources.Azure` version `1.15.0-beta.2`.

The fix (#4121) introduce changes that introduce limits to `HttpClient` requests so that the response body is streamed rather than buffered entirely in memory. Responses greater than 4 MiB are ignored.

### Workarounds

- Disable the Azure VM resource detector.
- Use network-level controls (firewall rules, mTLS, service mesh) to prevent Man-in-the-Middle (MitM) attacks on the Azure VM instance metadata endpoint.

### References

- [#4121](https://github.com/open-telemetry/opentelemetry-dotnet-contrib/pull/4121)

## References
- https://github.com/open-telemetry/opentelemetry-dotnet-contrib/security/advisories/GHSA-vc24-j8c5-2vw4
- https://nvd.nist.gov/vuln/detail/CVE-2026-41483
- https://github.com/open-telemetry/opentelemetry-dotnet-contrib/pull/4121
- https://github.com/open-telemetry/opentelemetry-dotnet-contrib/commit/9d8a364af919f62c088edd641c554cb720198964
- https://github.com/open-telemetry/opentelemetry-dotnet-contrib
