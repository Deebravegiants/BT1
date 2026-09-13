# [M] Ella Core Panics Upon NGAP handover failure

## Summary
Severity: Medium
Advisory: GHSA-6gm8-3g4h-w82m
CVE: CVE-2026-34761
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-6gm8-3g4h-w82m
Type: github-advisory

## Affected
- Go: `github.com/ellanetworks/core` — affected >=0 <1.8.0

## Details
## Summary

Ella Core panics when processing a NGAP handover failure message.

## Impact

If an attacker can force a gNodeB to send NGAP handover failure messages to Ella Core, the process will crash, thereby disrupting service for all connected subscribers.

## Fix 

Improve guards in NGAP handover handlers.

## References
- https://github.com/ellanetworks/core/security/advisories/GHSA-6gm8-3g4h-w82m
- https://nvd.nist.gov/vuln/detail/CVE-2026-34761
- https://github.com/ellanetworks/core
- https://github.com/ellanetworks/core/releases/tag/v1.8.0
