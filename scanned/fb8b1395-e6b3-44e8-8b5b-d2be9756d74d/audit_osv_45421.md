# [M] JLSEC-2026-1146

## Summary
Severity: Medium
Advisory: JLSEC-2026-1146
Ecosystem: Julia
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1146
Type: osv

## Affected
- Julia: `nats_server_jll` — affected >=0 <2.14.3+0

## Details
NATS Server is a high-performance server for NATS.io, the cloud and edge native messaging system. Prior to 2.14.3 and 2.12.12, MQTT retained message delivery and QoS1+ durable replay could deliver messages whose original topics matched a subscriber configured subscribe deny rule because these delivery paths did not consistently recheck the concrete original topic before sending the MQTT PUBLISH to the subscriber. This issue is fixed in versions 2.14.3 and 2.12.12.

## References
- https://github.com/nats-io/nats-server/commit/181b1f51f40b9954c57e9d478e051fb257679356
- https://github.com/nats-io/nats-server/commit/1c429b6fdc5afd4188cc5faf1127f6334896cd87
- https://github.com/nats-io/nats-server/releases/tag/v2.12.12
- https://github.com/nats-io/nats-server/releases/tag/v2.14.3
- https://github.com/nats-io/nats-server/security/advisories/GHSA-7qmq-8cc4-hxwg
