# [M] Ella Core panics when processing a crafted NGAP LocationReport message

## Summary
Severity: Medium
Advisory: GHSA-f2f3-9cx3-wcmf
CVE: CVE-2026-33903
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-f2f3-9cx3-wcmf
Type: github-advisory

## Affected
- Go: `github.com/ellanetworks/core` — affected >=0 <1.7.0

## Details
## Summary

Ella Core panics when processing a specially crafted NGAP LocationReport message.

## Impact

An attacker able to send crafted NGAP messages to Ella Core can crash the process, causing service disruption for all connected subscribers.

## Fix 

Add guards in NGAP Location Report handler.

## References
- https://github.com/ellanetworks/core/security/advisories/GHSA-f2f3-9cx3-wcmf
- https://nvd.nist.gov/vuln/detail/CVE-2026-33903
- https://github.com/ellanetworks/core/commit/ec77a2ad4508f8488cb356fd45b2f1efd92587f8
- https://github.com/ellanetworks/core
- https://github.com/ellanetworks/core/releases/tag/v1.7.0
