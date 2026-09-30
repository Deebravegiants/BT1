# [H] OpenClaw: Control UI locality spoofing could mint a durable admin device token

## Summary
Severity: High
Advisory: GHSA-chr9-m4q2-76hw
CVE: CVE-2026-53817
CWE: CWE-284, CWE-287, CWE-290, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-chr9-m4q2-76hw
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.22

## Details
### Summary

In affected LAN/shared-token Control UI deployments, a caller could spoof locality information used during Control UI pairing and obtain a durable admin-capable device token.

This issue is limited to deployments where the caller already has the network/authentication foothold needed to reach the Control UI pairing path. It is not an unauthenticated internet exposure issue.

### Affected configurations

This affects configurations such as LAN-bound gateways or shared-token Control UI access where locality signals were accepted as sufficient for pairing decisions.

### Impact

A temporary or shared Control UI access path could be turned into a persistent admin device token. That token could remain useful after the shared gateway token was rotated, unless the paired device was removed.

The issue is a pairing/locality validation problem: locality-derived trust was stronger than it should have been.

### Patched Versions

The first stable patched version is `2026.5.22`.

### Mitigations

Upgrade to `openclaw@2026.5.22` or later. For older deployments, remove unexpected paired devices and avoid exposing Control UI pairing paths on networks with untrusted clients.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-chr9-m4q2-76hw
- https://nvd.nist.gov/vuln/detail/CVE-2026-53817
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-control-ui-locality-spoofing-in-device-pairing
