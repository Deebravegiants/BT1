# [M] Ella Core panics on malformed ULNASTransport Message without a Request Type

## Summary
Severity: Medium
Advisory: GHSA-3366-gw57-fcm5
CVE: CVE-2026-33283
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-3366-gw57-fcm5
Type: github-advisory

## Affected
- Go: `github.com/ellanetworks/core` — affected >=0 <1.6.0

## Details
## Summary
Ella Core panics when processing malformed UL NAS Transport NAS messages without a Request Type.

## Impact
An attacker able to send crafted NAS messages to Ella Core can crash the process, causing service disruption for all connected subscribers. No authentication is required.

## Fix
Add a guard when receiving an UL NAS Message without a Request Type given no SM Context.

## References
- https://github.com/ellanetworks/core/security/advisories/GHSA-3366-gw57-fcm5
- https://nvd.nist.gov/vuln/detail/CVE-2026-33283
- https://github.com/ellanetworks/core
