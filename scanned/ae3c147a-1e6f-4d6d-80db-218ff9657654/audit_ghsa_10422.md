# [M] Tesla Fleet Telemetry allows spoofing telemetry for arbitrary vehicles via compromised vehicle credentials

## Summary
Severity: Medium
Advisory: GHSA-prxj-3gcv-cqrh
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-prxj-3gcv-cqrh
Type: github-advisory

## Affected
- Go: `github.com/teslamotors/fleet-telemetry` — affected >=0 <0.9.0

## Details
### Summary
A vulnerability in vehicle authentication allows  threat actor with valid client credentials (i.e., a private key and certificate from a rooted infotainment system) to impersonate arbitrary VINs when authenticating to the telemetry server.

### Impact
The attacker would be able to submit falsified telemetry records for arbitrary VINs.

## References
- https://github.com/teslamotors/fleet-telemetry/security/advisories/GHSA-prxj-3gcv-cqrh
- https://github.com/teslamotors/fleet-telemetry/commit/d5ca0dab55812029fd38eb77f079f74ce4f47286
- https://github.com/teslamotors/fleet-telemetry
