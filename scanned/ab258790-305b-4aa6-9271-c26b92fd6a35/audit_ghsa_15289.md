# [M] open-telemetry has an Observable Timing Discrepancy

## Summary
Severity: Medium
Advisory: GHSA-rfxf-mf63-cpqv
CVE: CVE-2024-42368
CWE: CWE-208
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-08-13
Source: https://github.com/advisories/GHSA-rfxf-mf63-cpqv
Type: github-advisory

## Affected
- Go: `github.com/open-telemetry/opentelemetry-collector-contrib/extension/bearertokenauthextension` — affected >=0.80.0 <0.107.0

## Details
### Summary

The bearertokenauth extension's server authenticator performs a simple, non-constant time string comparison of the received & configured bearer tokens.

### Details

https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/9128a9258fe1fee36f198f97b1e3371fc7b77a93/extension/bearertokenauthextension/bearertokenauth.go#L189-L196

For background on the type of vulnerability, see https://ropesec.com/articles/timing-attacks/.

### Impact

This impacts anyone using the `bearertokenauth` server authenticator. Malicious clients with network access to the collector may perform a timing attack against a collector with this authenticator to guess the configured token, by iteratively sending tokens and comparing the response time. This would allow an attacker to introduce fabricated or bad data into the collector's telemetry pipeline.

### Fix

The observable timing vulnerability was fixed by @axw in v0.107.0 (PR https://github.com/open-telemetry/opentelemetry-collector-contrib/pull/34516) by using constant-time comparison.

### Workarounds

- upgrade to v0.107.0 or above, or, if you're unable to upgrade at this time,
- don't expose the receiver using `bearertokenauth` to network segments accessible by potential attackers, or
- change the receiver to use a different authentication extension instead, or
- disable the receiver relying on `bearertokenauth`

## References
- https://github.com/open-telemetry/opentelemetry-collector-contrib/security/advisories/GHSA-rfxf-mf63-cpqv
- https://nvd.nist.gov/vuln/detail/CVE-2024-42368
- https://github.com/open-telemetry/opentelemetry-collector-contrib/pull/34516
- https://github.com/open-telemetry/opentelemetry-collector-contrib/commit/c9bd3eff0bb357d9c812a0d8defd3b09db95699a
- https://github.com/open-telemetry/opentelemetry-collector-contrib
