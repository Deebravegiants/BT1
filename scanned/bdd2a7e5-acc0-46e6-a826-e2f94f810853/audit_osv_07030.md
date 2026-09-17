# [M] NATS Server: Incomplete fix for CVE-2026-33249: Leaf node connections bypass Nats-Trace-Dest permission check

## Summary
Severity: Medium
Advisory: BIT-nats-2026-58254
Aliases: CVE-2026-58254, GHSA-p3j5-5hrq-p75h
Ecosystem: Bitnami
Published: 2026-07-14
Source: https://osv.dev/vulnerability/BIT-nats-2026-58254
Type: osv

## Affected
- Bitnami: `nats` — affected >=2.14.0 <2.14.3

## Details
NATS Server is a high-performance server for NATS.io, the cloud and edge native messaging system. Prior to 2.14.3 and 2.12.8, message trace destination checks were applied to ordinary client connections but not consistently to messages arriving through leafnode connections, allowing a leafnode operator to send trace events to subjects that would not otherwise be permitted and to use trace-only behavior to prevent normal delivery or storage of affected messages. This issue is fixed in versions 2.14.3 and 2.12.8.

## References
- https://github.com/nats-io/nats-server/commit/cbe845932980b71563efac5cfa4cc751c88936cd
- https://github.com/nats-io/nats-server/releases/tag/v2.12.8
- https://github.com/nats-io/nats-server/releases/tag/v2.14.3
- https://github.com/nats-io/nats-server/security/advisories/GHSA-p3j5-5hrq-p75h
- https://nvd.nist.gov/vuln/detail/CVE-2026-58254
