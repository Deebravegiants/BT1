# [H] redis-server use-after-free in unblock client flow may allow remote code execution

## Summary
Severity: High
Advisory: BIT-keydb-2026-23479
Aliases: BIT-redis-2026-23479, BIT-valkey-2026-23479, CVE-2026-23479, GHSA-93m2-935m-8rj3
Ecosystem: Bitnami
Published: 2026-05-07
Source: https://osv.dev/vulnerability/BIT-keydb-2026-23479
Type: osv

## Affected
- Bitnami: `keydb` — affected >=8.5.0 <8.6.3

## Details
Redis is an in-memory data structure store. In redis-server from 7.2.0 until 8.6.3, the unblock client flow does not handle an error return from `processCommandAndResetClient` when re-executing a blocked command. If a blocked client is evicted during this flow, an authenticated attacker can trigger a use-after-free that may lead to remote code execution. This has been patched in version 8.6.3.

## References
- https://github.com/redis/redis/releases/tag/8.6.3
- https://github.com/redis/redis/security/advisories/GHSA-93m2-935m-8rj3
- https://nvd.nist.gov/vuln/detail/CVE-2026-23479
- https://access.redhat.com/errata/RHSA-2026:25216
- https://access.redhat.com/errata/RHSA-2026:25219
- https://access.redhat.com/errata/RHSA-2026:25925
- https://access.redhat.com/errata/RHSA-2026:26306
- https://access.redhat.com/errata/RHSA-2026:26540
- https://access.redhat.com/security/cve/CVE-2026-23479
- https://bugzilla.redhat.com/show_bug.cgi?id=2466780
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-23479.json
- https://access.redhat.com/errata/RHSA-2026:14316
- https://access.redhat.com/errata/RHSA-2026:7662
