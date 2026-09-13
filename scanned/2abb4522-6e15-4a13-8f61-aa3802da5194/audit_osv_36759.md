# [M] nanomq: OOB Read / Crash (DoS) via Malformed MQTT Remaining Length over WebSocket

## Summary
Severity: Medium
Advisory: CVE-2026-25627
Aliases: GHSA-w4rh-v3h2-j29x
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-25627
Type: osv

## Details
NanoMQ MQTT Broker (NanoMQ) is an all-around Edge Messaging Platform. Prior to version 0.24.8, NanoMQ’s MQTT-over-WebSocket transport can be crashed by sending an MQTT packet with a deliberately large Remaining Length in the fixed header while providing a much shorter actual payload. The code path copies Remaining Length bytes without verifying that the current receive buffer contains that many bytes, resulting in an out-of-bounds read (ASAN reports OOB / crash). This is remotely triggerable over the WebSocket listener. This issue has been patched in version 0.24.8.

## References
- https://github.com/nanomq/nanomq/releases/tag/0.24.8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25627.json
- https://github.com/nanomq/nanomq/security/advisories/GHSA-w4rh-v3h2-j29x
- https://nvd.nist.gov/vuln/detail/CVE-2026-25627
- https://github.com/nanomq/NanoNNG/commit/e80b30bad6d855593a68d18f2785bfaca6faf09e
- https://github.com/nanomq/NanoNNG/pull/1405
