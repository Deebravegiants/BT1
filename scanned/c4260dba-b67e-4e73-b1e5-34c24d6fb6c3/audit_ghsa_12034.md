# [H] Ella Core panics on malformed NGAP Location Report

## Summary
Severity: High
Advisory: GHSA-826q-wrq4-p23x
CVE: CVE-2026-33282
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-826q-wrq4-p23x
Type: github-advisory

## Affected
- Go: `github.com/ellanetworks/core` — affected >=0 <1.6.0

## Details
## Summary

Ella Core panics when processing a malformed NGAP LocationReport message with  `ue-presence-in-area-of-interest` event type and omitting the optional `UEPresenceInAreaOfInterestList` IE.

## Impact
An attacker able to send crafted NGAP messages to Ella Core can crash the process, causing service disruption for all connected subscribers. No authentication is required.

## Fix
Added IE presence verification to NGAP message handling.

## References
- https://github.com/ellanetworks/core/security/advisories/GHSA-826q-wrq4-p23x
- https://nvd.nist.gov/vuln/detail/CVE-2026-33282
- https://github.com/ellanetworks/core
