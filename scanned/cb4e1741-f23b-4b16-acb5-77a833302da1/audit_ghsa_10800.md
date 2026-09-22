# [M] OpenTelemetry.Sampler.AWS & OpenTelemetry.Resources.AWS have unbounded HTTP response body reads

## Summary
Severity: Medium
Advisory: GHSA-28xm-prxc-5866
CVE: CVE-2026-41173
CWE: CWE-770
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-23
Source: https://github.com/advisories/GHSA-28xm-prxc-5866
Type: github-advisory

## Affected
- NuGet: `OpenTelemetry.Sampler.AWS` — affected >=0 <0.1.0-alpha.8
- NuGet: `OpenTelemetry.Resources.AWS` — affected >=0 <1.15.1

## Details
### Summary

`OpenTelemetry.Sampler.AWS` reads unbounded HTTP response bodies from a configured AWS X-Ray remote sampling endpoint into memory.

`OpenTelemetry.Resources.AWS` reads unbounded HTTP response bodies from a configured AWS EC2/ECS/EKS remote instance metadata service endpoint into memory.

Both of these would allow an attacker-controlled endpoint or be acting as a Man-in-the-Middle (MitM) to cause excessive memory allocation and possible process termination (via Out of Memory (OOM)).

### Details

#### OpenTelemetry.Sampler.AWS

`AWSXRaySamplerClient.DoRequestAsync` called `HttpClient.SendAsync` followed by `ReadAsStringAsync()`, which materializes the entire HTTP response body into a single in-memory string with no size limit. The sampling endpoint is configurable via `AWSXRayRemoteSamplerBuilder.SetEndpoint` (default: `http://localhost:2000`).

An attacker who controls the configured endpoint, or who can intercept traffic to it (MitM), can return an arbitrarily large response body. This causes unbounded heap allocation in the consuming process, leading to high transient memory pressure, garbage-collection stalls, or an `OutOfMemoryException` that terminates the process.

#### OpenTelemetry.Resources.AWS

The [`AWSEC2Detector`](https://github.com/open-telemetry/opentelemetry-dotnet-contrib/blob/171c6b81f88831641b56b470e6f92862e605013d/src/OpenTelemetry.Resources.AWS/AWSEC2Detector.cs), [`AWSECSDetector`](https://github.com/open-telemetry/opentelemetry-dotnet-contrib/blob/171c6b81f88831641b56b470e6f92862e605013d/src/OpenTelemetry.Resources.AWS/AWSECSDetector.cs) and [`AWSEKSDetector`](https://github.com/open-telemetry/opentelemetry-dotnet-contrib/blob/171c6b81f88831641b56b470e6f92862e605013d/src/OpenTelemetry.Resources.AWS/AWSEKSDetector.cs) classes all make HTTP requests to the relevant AWS metadata service (`http://169.254.169.254`, `ECS_CONTAINER_METADATA_URI`/`ECS_CONTAINER_METADATA_URI_V4` or `https://kubernetes.default.svc` respectively) to obtain metadata about the running process and its infrastructure.

An attacker who controls the configured endpoint(s), or who can intercept traffic to them (MiTM), can return an arbitrarily large response body. This causes unbounded heap allocation in the consuming process, leading to high transient memory pressure, garbage-collection stalls, or an `OutOfMemoryException` that terminates the process.

### Impact

Denial of Service (DoS). An attacker can destabilize or crash the application by forcing unbounded memory allocation through the X-Ray sampling and/or EC2/ECS/EKS HTTP response paths.

### Mitigating Factors

- The default X-Ray sampling endpoint is `http://localhost:2000`, which limits remote exposure in default configurations.
- Risk increases materially when operators configure the sampler to point at a remote or untrusted endpoint.

### Patches

Fixed in `OpenTelemetry.Sampler.AWS` version `0.1.0-alpha.8` and `OpenTelemetry.Resources.AWS` version `1.15.1`.

The fixes (#4100, #4122) introduce changes that introduce limits to `HttpClient` requests so that the response body is streamed rather than buffered entirely in memory.

### Workarounds

- Ensure the X-Ray sampling endpoint (`http://localhost:2000` by default) is not accessible to untrusted parties.
- Use network-level controls (firewall rules, mTLS, service mesh) to prevent Man-in-the-Middle (MitM) attacks on the sampling endpoint and/or EC2/ECS/EKS connection.
- If using a remote endpoint, place it behind a reverse proxy that enforces a response body size limit.

## References
- https://github.com/open-telemetry/opentelemetry-dotnet-contrib/security/advisories/GHSA-28xm-prxc-5866
- https://nvd.nist.gov/vuln/detail/CVE-2026-41173
- https://github.com/open-telemetry/opentelemetry-dotnet-contrib/pull/4100
- https://github.com/open-telemetry/opentelemetry-dotnet-contrib/pull/4122
- https://github.com/open-telemetry/opentelemetry-dotnet-contrib
