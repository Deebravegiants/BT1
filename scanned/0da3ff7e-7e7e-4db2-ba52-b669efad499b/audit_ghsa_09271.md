# [H] Ella Core Vulnerable to UE Downlink Redirection via Forged PDUSessionResourceSetupResponse

## Summary
Severity: High
Advisory: GHSA-qfxw-v8qx-vj3v
CVE: CVE-2026-44473
CWE: CWE-358, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-qfxw-v8qx-vj3v
Type: github-advisory

## Affected
- Go: `github.com/ellanetworks/core` — affected >=0 <1.10.0

## Details
## Summary

A radio with a valid NG Setup can send a forged PDUSessionResourceSetupResponse carrying any UE's AMF-UE-NGAP-ID. Ella Core does not verify the message arrived on the SCTP association bound to that UE's logical NG-connection, then creates a GTP tunnel towards that radio.

## Impact

Downlink user-plane traffic for the targeted UE is redirected to the attacker's radio.

## Fix

UE context lookups are now scoped to the sending radio's SCTP association.

## References
- https://github.com/ellanetworks/core/security/advisories/GHSA-qfxw-v8qx-vj3v
- https://nvd.nist.gov/vuln/detail/CVE-2026-44473
- https://github.com/ellanetworks/core
