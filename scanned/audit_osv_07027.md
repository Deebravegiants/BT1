# [M] NATS Server: Queue Subscribe Authz Bypass

## Summary
Severity: Medium
Advisory: BIT-nats-2026-58251
Aliases: CVE-2026-58251, GHSA-jx8g-9g95-6322
Ecosystem: Bitnami
Published: 2026-07-14
Source: https://osv.dev/vulnerability/BIT-nats-2026-58251
Type: osv

## Affected
- Bitnami: `nats` — affected >=2.12.0 <2.12.7

## Details
NATS Server is a high-performance server for NATS.io, the cloud and edge native messaging system. Prior to 2.14.0, 2.12.7, and 2.11.16, an authenticated user with subscription deny permissions could bypass a plain subject deny rule by using a queue subscription, because queue-specific deny evaluation could override the plain subject deny result when the queue name itself was not denied. This issue is fixed in versions 2.14.0, 2.12.7, and 2.11.16.

## References
- https://github.com/nats-io/nats-server/commit/013586288078def45a6788096924eb4d150db65c
- https://github.com/nats-io/nats-server/commit/79c2f6e9ff87f594596337b6427dda85c38d1fe1
- https://github.com/nats-io/nats-server/commit/b9ffb63b85e7db3d25a13b2e234f5f7f7c13164d
- https://github.com/nats-io/nats-server/releases/tag/v2.11.16
- https://github.com/nats-io/nats-server/releases/tag/v2.12.7
- https://github.com/nats-io/nats-server/releases/tag/v2.14.0
- https://github.com/nats-io/nats-server/security/advisories/GHSA-jx8g-9g95-6322
- https://nvd.nist.gov/vuln/detail/CVE-2026-58251
