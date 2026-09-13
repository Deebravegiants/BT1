# [H] NATS Server: MQTT SUBSCRIBE Protocol Injection via Leaf Node/Route Forwarding allows arbitrary NATS command injection

## Summary
Severity: High
Advisory: BIT-nats-2026-58213
Aliases: CVE-2026-58213, GHSA-qrcv-3558-gj4f
Ecosystem: Bitnami
Published: 2026-07-14
Source: https://osv.dev/vulnerability/BIT-nats-2026-58213
Type: osv

## Affected
- Bitnami: `nats` — affected >=2.14.0 <2.14.1

## Details
NATS Server is a high-performance server for NATS.io, the cloud and edge native messaging system. Prior to 2.14.1 and 2.12.9, an MQTT client could include protocol control characters in subscription filters that were later forwarded as NATS protocol data to route or leafnode connections, corrupting the forwarded protocol stream and allowing injection of unintended NATS protocol operations. This issue is fixed in versions 2.14.1 and 2.12.9.

## References
- https://github.com/nats-io/nats-server/commit/366837cfc65ab9ccb4f98193c65e8daf238582d8
- https://github.com/nats-io/nats-server/commit/64ebae40051ee497c481e10f316238faf0de1736
- https://github.com/nats-io/nats-server/commit/f14856b9e57a36818f43851cb69b6e33670885c9
- https://github.com/nats-io/nats-server/pull/8163
- https://github.com/nats-io/nats-server/pull/8164
- https://github.com/nats-io/nats-server/releases/tag/v2.12.9
- https://github.com/nats-io/nats-server/releases/tag/v2.14.1
- https://github.com/nats-io/nats-server/security/advisories/GHSA-qrcv-3558-gj4f
- https://nvd.nist.gov/vuln/detail/CVE-2026-58213
