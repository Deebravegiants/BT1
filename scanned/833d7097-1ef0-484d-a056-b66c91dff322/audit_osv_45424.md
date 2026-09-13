# [M] JLSEC-2026-1149

## Summary
Severity: Medium
Advisory: JLSEC-2026-1149
Ecosystem: Julia
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1149
Type: osv

## Affected
- Julia: `nats_server_jll` — affected >=0 <2.14.3+0

## Details
NATS Server is a high-performance server for NATS.io, the cloud and edge native messaging system. Prior to 2.14.3 and 2.12.12, an authenticated MQTT client could subscribe to the internal `$MQTT.deliver.pubrel` subject family, bypassing configured subscribe permissions and exposing MQTT QoS2 protocol metadata for sessions in the account. This issue is fixed in versions 2.14.3 and 2.12.12.

## References
- https://github.com/nats-io/nats-server/commit/297b166be60fe13144084eed4b25201ead03204a
- https://github.com/nats-io/nats-server/commit/34b09657bb596d5f850eaa5cfc97ea6b2f989a97
- https://github.com/nats-io/nats-server/releases/tag/v2.12.12
- https://github.com/nats-io/nats-server/releases/tag/v2.14.3
- https://github.com/nats-io/nats-server/security/advisories/GHSA-4g68-3pwx-5vfj
