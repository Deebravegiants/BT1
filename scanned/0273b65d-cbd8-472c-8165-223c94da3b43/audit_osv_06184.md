# [H] redis-server RESTORE invalid memory access may allow remote code execution

## Summary
Severity: High
Advisory: BIT-keydb-2026-25243
Aliases: BIT-redis-2026-25243, BIT-valkey-2026-25243, CVE-2026-25243, GHSA-c8h9-259x-jff4
Ecosystem: Bitnami
Published: 2026-05-07
Source: https://osv.dev/vulnerability/BIT-keydb-2026-25243
Type: osv

## Affected
- Bitnami: `keydb` — affected >=8.5.0 <8.6.3

## Details
Redis is an in-memory data structure store. In versions of redis-server up to 8.6.3, the RESTORE command does not properly validate serialized values. An authenticated attacker with permission to execute RESTORE can supply a crafted serialized payload that triggers invalid memory access and may lead to remote code execution. A workaround is to restrict access to the RESTORE command with ACL rules. This is patched in version 8.6.3.

## References
- https://github.com/redis/redis/releases/tag/8.6.3
- https://github.com/redis/redis/security/advisories/GHSA-c8h9-259x-jff4
- https://nvd.nist.gov/vuln/detail/CVE-2026-25243
- https://access.redhat.com/errata/RHSA-2026:23229
- https://access.redhat.com/errata/RHSA-2026:25216
- https://access.redhat.com/errata/RHSA-2026:25219
- https://access.redhat.com/errata/RHSA-2026:25925
- https://access.redhat.com/errata/RHSA-2026:26008
- https://access.redhat.com/errata/RHSA-2026:26233
- https://access.redhat.com/errata/RHSA-2026:26306
- https://access.redhat.com/errata/RHSA-2026:26540
- https://access.redhat.com/errata/RHSA-2026:27716
- https://access.redhat.com/errata/RHSA-2026:27787
- https://access.redhat.com/errata/RHSA-2026:28139
- https://access.redhat.com/errata/RHSA-2026:28142
- https://access.redhat.com/errata/RHSA-2026:29817
- https://access.redhat.com/errata/RHSA-2026:33427
- https://access.redhat.com/security/cve/CVE-2026-25243
- https://bugzilla.redhat.com/show_bug.cgi?id=2466828
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-25243.json
