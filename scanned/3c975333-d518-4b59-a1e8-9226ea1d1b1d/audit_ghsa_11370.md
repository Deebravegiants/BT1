# [M] Ella Core panics on invalid PDU Session IDs in NGAP messages

## Summary
Severity: Medium
Advisory: GHSA-q669-4gmv-g8mf
CVE: CVE-2026-33281
CWE: CWE-129
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-q669-4gmv-g8mf
Type: github-advisory

## Affected
- Go: `github.com/ellanetworks/core` — affected >=0 <1.6.0

## Details
## Summary

Ella Core panics when processing NGAP messages with invalid PDU Session IDs outside of 1-15.

## Impact
An attacker able to send crafted NGAP messages to Ella Core can crash the process, causing service disruption for all connected subscribers. No authentication is required.

## Fix
Added PDU Session ID validations during NGAP message handling.

## References
- https://github.com/ellanetworks/core/security/advisories/GHSA-q669-4gmv-g8mf
- https://nvd.nist.gov/vuln/detail/CVE-2026-33281
- https://github.com/ellanetworks/core
