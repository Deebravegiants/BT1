# [H] NATS Server: MQTT partial CONNECT packets can exhaust pre-auth memory

## Summary
Severity: High
Advisory: BIT-nats-2026-58210
Aliases: CVE-2026-58210, GHSA-r72h-j7qq-v6qg
Ecosystem: Bitnami
Published: 2026-07-14
Source: https://osv.dev/vulnerability/BIT-nats-2026-58210
Type: osv

## Affected
- Bitnami: `nats` — affected >=2.14.0 <2.14.3

## Details
NATS Server is a high-performance server for NATS.io, the cloud and edge native messaging system. Prior to 2.14.3 and 2.12.12, an unauthenticated MQTT client could cause the server to retain large incomplete MQTT CONNECT packets before authentication completed, consuming server memory while the parser waited for the advertised MQTT packet length. This issue is fixed in versions 2.14.3 and 2.12.12.

## References
- https://github.com/nats-io/nats-server/commit/bce9ef39469e610aeddb819194ceb7f7edfc0861
- https://github.com/nats-io/nats-server/commit/e016e47bbf70304945f2ae9dc397e4862adefaf5
- https://github.com/nats-io/nats-server/releases/tag/v2.12.12
- https://github.com/nats-io/nats-server/releases/tag/v2.14.3
- https://github.com/nats-io/nats-server/security/advisories/GHSA-r72h-j7qq-v6qg
- https://nvd.nist.gov/vuln/detail/CVE-2026-58210
