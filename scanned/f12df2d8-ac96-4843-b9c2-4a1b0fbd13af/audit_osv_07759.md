# [H] Valkey: UAF in stream deserialization may lead to remote code execution

## Summary
Severity: High
Advisory: BIT-valkey-2026-63639
Aliases: CVE-2026-63639, GHSA-mvcj-73cw-22m4
Ecosystem: Bitnami
Published: 2026-08-24
Source: https://osv.dev/vulnerability/BIT-valkey-2026-63639
Type: osv

## Affected
- Bitnami: `valkey` — affected >=9.1.0 <9.1.1

## Details
Valkey is a distributed key-value database. Prior to 7.2.14, 8.0.10, 8.1.9, 9.0.5, and 9.1.1, Valkey's RESTORE command accepts a malformed RDB stream payload that assigns one Pending Entry List NACK to multiple consumers during stream consumer-group deserialization, causing a use-after-free when one consumer is deleted while another still references the shared NACK and potentially allowing remote code execution. This issue is fixed in versions 7.2.14, 8.0.10, 8.1.9, 9.0.5, and 9.1.1.

## References
- https://github.com/valkey-io/valkey/commit/06bc7768fe609f2054e69ccedefe7628f5675da9
- https://github.com/valkey-io/valkey/commit/509cb3c74e8cbc9c0498ebe8b6c93dcd605e7271
- https://github.com/valkey-io/valkey/commit/98465eaffe3f95524a5046318bfbc4bdb9798291
- https://github.com/valkey-io/valkey/commit/e95911d4d65be8789fa3705f44d7ed1e65378445
- https://github.com/valkey-io/valkey/commit/f8d2027e8d4df790ac04974bf606408c8ea62778
- https://github.com/valkey-io/valkey/pull/4073
- https://github.com/valkey-io/valkey/releases/tag/7.2.14
- https://github.com/valkey-io/valkey/releases/tag/8.0.10
- https://github.com/valkey-io/valkey/releases/tag/8.1.9
- https://github.com/valkey-io/valkey/releases/tag/9.0.5
- https://github.com/valkey-io/valkey/releases/tag/9.1.1
- https://github.com/valkey-io/valkey/security/advisories/GHSA-mvcj-73cw-22m4
- https://nvd.nist.gov/vuln/detail/CVE-2026-63639
