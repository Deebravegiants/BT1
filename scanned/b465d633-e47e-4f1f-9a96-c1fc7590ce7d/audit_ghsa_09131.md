# [M] OpAMP client reads unbounded HTTP response bodies

## Summary
Severity: Medium
Advisory: GHSA-w2jh-77fq-7gp8
CVE: CVE-2026-42348
CWE: CWE-789
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-w2jh-77fq-7gp8
Type: github-advisory

## Affected
- NuGet: `OpenTelemetry.OpAmp.Client` — affected >=0 <0.2.0-alpha.1

## Details
### Summary

When receiving responses from the OpAMP server over HTTP, the OpAMP client allocates an unbounded buffer to read all bytes from the server, with no upper-bound on the number of bytes consumed.

This could cause memory exhaustion in the consuming application if the configured OpAMP server is attacker-controlled (or a network attacker can MitM the connection) and an extremely large body is returned in the response. 

### Details

[#2926](https://github.com/open-telemetry/opentelemetry-dotnet-contrib/pull/2926) introduced the initial HTTP transport components which uses `ReadAsByteArrayAsync` to copy the `HttpResponseMessage.Content` into a byte array. This code path allows an unbounded read of the entire HTTP response message.

### Impact

If an application using the OpAMP client is configured to use an OpAMP server that is attacker-controlled (or a network attacker can MitM the connection) and an extremely large body is returned in the response, the application could have its memory exhausted and create a denial-of-service condition.

### Mitigation

The application's configured OpAMP server needs to behave maliciously. If the OpAMP server is a well-behaved implementation, response bodies should not be excessively large.

### Workarounds

None known.

### Remediation

[#4116](https://github.com/open-telemetry/opentelemetry-dotnet-contrib/pull/4116) updates the OpAMP client HTTP transport to limit the maximum size of responses to 128KB.

### Resources

- [#2926](https://github.com/open-telemetry/opentelemetry-dotnet-contrib/pull/2926)
- [#4116](https://github.com/open-telemetry/opentelemetry-dotnet-contrib/pull/4116)
- [CWE-789](https://cwe.mitre.org/data/definitions/789.html)

## References
- https://github.com/open-telemetry/opentelemetry-dotnet-contrib/security/advisories/GHSA-w2jh-77fq-7gp8
- https://nvd.nist.gov/vuln/detail/CVE-2026-42348
- https://github.com/open-telemetry/opentelemetry-dotnet-contrib/pull/4116
- https://github.com/open-telemetry/opentelemetry-dotnet-contrib/commit/bf1fad4fa298ff451cda0efb0ee9c7a7eb46212a
- https://github.com/open-telemetry/opentelemetry-dotnet-contrib
