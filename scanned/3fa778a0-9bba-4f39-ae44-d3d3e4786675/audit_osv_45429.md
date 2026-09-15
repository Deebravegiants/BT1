# [M] JLSEC-2026-1154

## Summary
Severity: Medium
Advisory: JLSEC-2026-1154
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1154
Type: osv

## Affected
- Julia: `nats_server_jll` — affected >=0 <2.14.3+0

## Details
NATS Server is a high-performance server for NATS.io, the cloud and edge native messaging system. Prior to 2.14.3 and 2.12.8, message trace destination checks were applied to ordinary client connections but not consistently to messages arriving through leafnode connections, allowing a leafnode operator to send trace events to subjects that would not otherwise be permitted and to use trace-only behavior to prevent normal delivery or storage of affected messages. This issue is fixed in versions 2.14.3 and 2.12.8.

## References
- https://github.com/nats-io/nats-server/commit/cbe845932980b71563efac5cfa4cc751c88936cd
- https://github.com/nats-io/nats-server/releases/tag/v2.12.8
- https://github.com/nats-io/nats-server/releases/tag/v2.14.3
- https://github.com/nats-io/nats-server/security/advisories/GHSA-p3j5-5hrq-p75h
