# [M] Ella Core: AMF DoS via malformed PathSwitchRequest with empty NR security capability bitstrings

## Summary
Severity: Medium
Advisory: GHSA-j478-p7vq-3347
CVE: CVE-2026-32320
CWE: CWE-125
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-j478-p7vq-3347
Type: github-advisory

## Affected
- Go: `github.com/ellanetworks/core` — affected >=0 <1.5.1

## Details
## Summary

Ella Core panics when processing a PathSwitchRequest containing UE Security Capabilities with zero-length NR encryption or integrity protection algorithm bitstrings, resulting in a denial of service.

## Impact

An attacker able to send crafted NGAP messages to Ella Core can crash the process, causing service disruption for all connected subscribers. No authentication is required.

## Fix

Added length validation on NR algorithm bitstrings before accessing them in the PathSwitchRequest handler.

## References
- https://github.com/ellanetworks/core/security/advisories/GHSA-j478-p7vq-3347
- https://nvd.nist.gov/vuln/detail/CVE-2026-32320
- https://github.com/ellanetworks/core
- https://github.com/ellanetworks/core/releases/tag/v1.5.1
- https://pkg.go.dev/vuln/GO-2026-4691
