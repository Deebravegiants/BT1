# [H] JLSEC-2026-1150

## Summary
Severity: High
Advisory: JLSEC-2026-1150
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1150
Type: osv

## Affected
- Julia: `nats_server_jll` — affected >=0 <2.14.3+0

## Details
NATS Server is a high-performance server for NATS.io, the cloud and edge native messaging system. Prior to 2.12.8 and 2.11.17, an unauthenticated peer with network access to a leafnode listener with compression enabled could crash the server during the pre-authentication leafnode handshake by sending repeated leafnode INFO protocol messages before authentication and account setup completed. This issue is fixed in versions 2.12.8 and 2.11.17.

## References
- https://github.com/nats-io/nats-server/commit/8dcb26eaea78fdcbe96dbee5986d6019fd5cb94a
- https://github.com/nats-io/nats-server/commit/fc5fe39177533e9dbdd651d2458285bfae1dde27
- https://github.com/nats-io/nats-server/releases/tag/v2.11.17
- https://github.com/nats-io/nats-server/releases/tag/v2.12.8
- https://github.com/nats-io/nats-server/security/advisories/GHSA-3g5q-cfh2-cq67
