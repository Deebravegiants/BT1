# [M] NATS Server: Subscribe Authz Bypass via Wildcard-Overlap

## Summary
Severity: Medium
Advisory: BIT-nats-2026-58252
Aliases: CVE-2026-58252, GHSA-wh7g-5m82-pmhr
Ecosystem: Bitnami
Published: 2026-07-14
Source: https://osv.dev/vulnerability/BIT-nats-2026-58252
Type: osv

## Affected
- Bitnami: `nats` — affected >=2.12.0 <2.12.7

## Details
NATS Server is a high-performance server for NATS.io, the cloud and edge native messaging system. Prior to 2.14.0, 2.12.7, and 2.11.16, an authenticated user could receive messages on denied subjects when a wildcard subscription overlapped with a configured wildcard deny rule but was not a subset of it, and queue subscriptions could also affect delivery to legitimate queue consumers. This issue is fixed in versions 2.14.0, 2.12.7, and 2.11.16.

## References
- https://github.com/nats-io/nats-server/commit/8ced85a11497f86704a95d960281480ce037386b
- https://github.com/nats-io/nats-server/commit/a42a6d1e258eb5c3a2190384d31965a4b715e854
- https://github.com/nats-io/nats-server/commit/e611ca9604697b02d8f22beb76037400a9cf72e6
- https://github.com/nats-io/nats-server/releases/tag/v2.11.16
- https://github.com/nats-io/nats-server/releases/tag/v2.12.7
- https://github.com/nats-io/nats-server/releases/tag/v2.14.0
- https://github.com/nats-io/nats-server/security/advisories/GHSA-wh7g-5m82-pmhr
- https://nvd.nist.gov/vuln/detail/CVE-2026-58252
