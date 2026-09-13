# [M] NATS Server: MQTT-over-WebSocket Path Can Crash WebSocket-Only JetStream Servers Before MQTT Is Enabled

## Summary
Severity: Medium
Advisory: CVE-2026-58208
Aliases: GHSA-p957-7v2w-g93g
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-58208
Type: osv

## Details
NATS Server is a high-performance server for NATS.io, the cloud and edge native messaging system. Prior to 2.14.3 and 2.12.12, a WebSocket listener could route requests for the MQTT-over-WebSocket path into MQTT handling even when MQTT was not configured, allowing an unauthenticated client with access to the WebSocket listener to reach uninitialized MQTT state and crash the server process. This issue is fixed in versions 2.14.3 and 2.12.12.

## References
- https://github.com/nats-io/nats-server/releases/tag/v2.12.12
- https://github.com/nats-io/nats-server/releases/tag/v2.14.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58208.json
- https://github.com/nats-io/nats-server/security/advisories/GHSA-p957-7v2w-g93g
- https://nvd.nist.gov/vuln/detail/CVE-2026-58208
- https://github.com/nats-io/nats-server/commit/73b3dd9a5ea0fa7bf08b702338676355b29b5fb4
- https://github.com/nats-io/nats-server/commit/837536b98b3a9280b993282155ff2bdd3ca38c30
