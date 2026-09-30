# [H] NATS Server: Pre-auth server crash via double INFO in leafnode handshake

## Summary
Severity: High
Advisory: BIT-nats-2026-58250
Aliases: CVE-2026-58250, GHSA-3g5q-cfh2-cq67
Ecosystem: Bitnami
Published: 2026-07-14
Source: https://osv.dev/vulnerability/BIT-nats-2026-58250
Type: osv

## Affected
- Bitnami: `nats` — affected >=2.12.0 <2.12.8

## Details
NATS Server is a high-performance server for NATS.io, the cloud and edge native messaging system. Prior to 2.12.8 and 2.11.17, an unauthenticated peer with network access to a leafnode listener with compression enabled could crash the server during the pre-authentication leafnode handshake by sending repeated leafnode INFO protocol messages before authentication and account setup completed. This issue is fixed in versions 2.12.8 and 2.11.17.

## References
- https://github.com/nats-io/nats-server/commit/8dcb26eaea78fdcbe96dbee5986d6019fd5cb94a
- https://github.com/nats-io/nats-server/commit/fc5fe39177533e9dbdd651d2458285bfae1dde27
- https://github.com/nats-io/nats-server/releases/tag/v2.11.17
- https://github.com/nats-io/nats-server/releases/tag/v2.12.8
- https://github.com/nats-io/nats-server/security/advisories/GHSA-3g5q-cfh2-cq67
- https://nvd.nist.gov/vuln/detail/CVE-2026-58250
