# [H] Steeltoe.Discovery.Eureka: Unrecognized DataCenterInfo.Name poisons entire registry fetch

## Summary
Severity: High
Advisory: GHSA-j8ph-6fxj-g533
CVE: CVE-2026-50196
CWE: CWE-20, CWE-400
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-j8ph-6fxj-g533
Type: github-advisory

## Affected
- NuGet: `Steeltoe.Discovery.Eureka` — affected >=4.0.0 <4.2.0
- NuGet: `Steeltoe.Discovery.Eureka` — affected >=0 <3.4.0

## Details
### Summary

`DataCenterInfo.FromJson` throws `ArgumentException` for any `name` value other than `"MyOwn"` or `"Amazon"`, despite the Java Eureka specification defining a third valid value: `"Netflix"`. The exception propagates through the entire registry deserialization chain and is swallowed by the periodic cache refresh task, leaving the local service registry permanently empty or stale.

### Impact

Any registration with an unrecognized `DataCenterInfo.name` permanently disables service discovery for every Steeltoe Eureka client connected to the same registry. New clients start with an empty registry and running clients stop refreshing. The outage persists until the triggering registration is removed.

Because `"Netflix"` is valid in the Java Eureka specification, a Java or Spring service in the same mesh can trigger this unintentionally.

### Affected configuration

- Application uses the Steeltoe Eureka client (`EurekaDiscoveryClient`).
- The registry contains at least one registration with a `DataCenterInfo.name` value other than `"MyOwn"` or `"Amazon"`.

### Mitigations

If an immediate upgrade is not possible, remove any registrations using unsupported `DataCenterInfo.name` values from the registry. In mixed Java/Spring and Steeltoe environments, audit for the `Netflix` data center type before deploying Steeltoe Eureka clients.

## References
- https://github.com/SteeltoeOSS/security-advisories/security/advisories/GHSA-j8ph-6fxj-g533
- https://nvd.nist.gov/vuln/detail/CVE-2026-50196
- https://github.com/SteeltoeOSS/Steeltoe/commit/b8ed8557bb595863e4f340051d16b26ba40a75f4
- https://github.com/SteeltoeOSS/Steeltoe/commit/c34a7399e808d0d11dd977460e81df1f2722df28
- https://github.com/SteeltoeOSS/Steeltoe
