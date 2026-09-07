# [M] Ella Core Panics during NAS Authentication Response/Failure with missing IEs

## Summary
Severity: Medium
Advisory: GHSA-55q8-2gwx-29pc
CVE: CVE-2026-33907
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-55q8-2gwx-29pc
Type: github-advisory

## Affected
- Go: `github.com/ellanetworks/core` — affected >=0 <1.7.0

## Details
## Summary

Ella Core panics when processing Authentication Response and Authentication Failure NAS message missing IEs. 

## Impact

An attacker able to send crafted NAS messages to Ella Core can crash the process, causing service disruption for all connected subscribers. No authentication is required.

## Fix

Added IE presence verification to NAS message handling.

## References
- https://github.com/ellanetworks/core/security/advisories/GHSA-55q8-2gwx-29pc
- https://nvd.nist.gov/vuln/detail/CVE-2026-33907
- https://github.com/ellanetworks/core/commit/52962660e3bd3e23c7e96b0da270ac1e0e705273
- https://github.com/ellanetworks/core
- https://github.com/ellanetworks/core/releases/tag/v1.7.0
