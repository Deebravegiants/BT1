# [M] Yamcs's WebSocket subscription handlers omit the privilege checks their REST siblings enforce

## Summary
Severity: Medium
Advisory: GHSA-fwww-cp23-7f5g
CVE: CVE-2026-55545
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-fwww-cp23-7f5g
Type: github-advisory

## Affected
- Maven: `org.yamcs:yamcs-core` — affected >=0 <5.12.8
- Maven: `org.yamcs:yamcs-core` — affected >=5.13.0 <5.13.2

## Details
**Asset / scope:** Yamcs 5.12.7 WebSocket topics (`packets`, `algorithm-status`, `mdb-changes`)

## Summary

Several WebSocket subscription handlers do not perform the privilege check that their REST counterparts
enforce, so a principal subscribing over WebSocket receives data the REST API would have scoped or denied.

## Root cause

- `packets` (`PacketsApi.subscribePackets`) performs no `ReadPacket` check, while the REST siblings do
  (`listPackets:128`, `streamPackets:256`, `subscribeContainers:538`). A principal with a narrow
  `ReadPacket` scope receives the raw binary of all TM packets on the processor.
- `algorithm-status` (`ProcessingApi.subscribeAlgorithmStatus`) performs no check, while REST
  `getAlgorithmStatus` enforces `checkObjectPrivileges(ReadAlgorithm, ...)` (`:467`).
- `mdb-changes` (`MdbOverrideApi.subscribeMdbChanges`) performs no check, while base MDB reads require
  `GetMissionDatabase`.

## Remediation

Bring each WebSocket subscription handler to parity with its REST sibling's privilege check
(`ReadPacket`, `ReadAlgorithm`, `GetMissionDatabase`). This is the same declarative fail-closed fix as
Report 1.

## Supporting material

Subsystem source audit of the WS-vs-REST authorization parity. Available on request.

--

## Disclosure and credit

This was found by Cipher / Causal Security - https://causalsecurity.com/. We are coordinating disclosure
via this report and request CVEs where you agree they qualify. We propose the 90-day window stated in your
security policy. We might publish a write-up after a fix and the agreed window.

## References
- https://github.com/yamcs/yamcs/security/advisories/GHSA-fwww-cp23-7f5g
- https://github.com/yamcs/yamcs/commit/0691731846c5a0aca81b88fabbd2cd51d56fe076
- https://github.com/yamcs/yamcs/commit/12864af555e6ca4941b01c1f1217859cc0492ce0
- https://github.com/yamcs/yamcs
- https://github.com/yamcs/yamcs/releases/tag/yamcs-5.12.8
- https://github.com/yamcs/yamcs/releases/tag/yamcs-5.13.2
