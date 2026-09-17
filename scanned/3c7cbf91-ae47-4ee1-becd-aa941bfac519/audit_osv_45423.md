# [H] JLSEC-2026-1148

## Summary
Severity: High
Advisory: JLSEC-2026-1148
Ecosystem: Julia
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1148
Type: osv

## Affected
- Julia: `nats_server_jll` — affected >=0 <2.14.3+0

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
