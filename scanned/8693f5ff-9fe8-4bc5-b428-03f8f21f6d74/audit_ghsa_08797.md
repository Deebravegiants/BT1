# [M] Ella Core has a UE Security Capability bypass on NGAP PathSwitchRequest

## Summary
Severity: Medium
Advisory: GHSA-pwfh-mqp3-pqwj
CVE: CVE-2026-44475
CWE: CWE-358
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-pwfh-mqp3-pqwj
Type: github-advisory

## Affected
- Go: `github.com/ellanetworks/core` — affected >=0 <1.10.0

## Details
## Summary

Ella Core does not verify the UE Security Capabilities received in NGAP PathSwitchRequest messages against its locally stored values. A malicious gNB can overwrite Ella Core's stored UE security capabilities for any UE with arbitrary values by sending a single crafted PathSwitchRequest.

## Impact

A gNB can corrupt Ella Core's stored UE security capabilities for a target UE.

## Fix

The PathSwitchRequest handler now compares the received UE Security Capabilities against Ella Core's locally stored values, preserves the stored values on mismatch, returns them in the PathSwitchRequestAcknowledge, and logs the event.

## References
- https://github.com/ellanetworks/core/security/advisories/GHSA-pwfh-mqp3-pqwj
- https://nvd.nist.gov/vuln/detail/CVE-2026-44475
- https://github.com/ellanetworks/core
