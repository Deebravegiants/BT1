# [H] Ella Core vulnerable to Unauthenticated AMF DoS via malformed InitialUEMessage with undersized integrity-protected NAS payload

## Summary
Severity: High
Advisory: GHSA-m9pm-w3gv-c68f
CVE: CVE-2026-32319
CWE: CWE-125
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-m9pm-w3gv-c68f
Type: github-advisory

## Affected
- Go: `github.com/ellanetworks/core` — affected >=0 <1.5.1

## Details
## Summary

Ella Core panics when processing a malformed integrity protected NGAP/NAS message with a length under 7 bytes.

## Impact

An attacker able to send crafted NAS messages to Ella Core can crash the process, causing service disruption for all connected subscribers. No authentication is required.

## Fix

Added length verification to NAS message handling.

## References
- https://github.com/ellanetworks/core/security/advisories/GHSA-m9pm-w3gv-c68f
- https://nvd.nist.gov/vuln/detail/CVE-2026-32319
- https://github.com/ellanetworks/core
- https://github.com/ellanetworks/core/releases/tag/v1.5.1
- https://pkg.go.dev/vuln/GO-2026-4692
