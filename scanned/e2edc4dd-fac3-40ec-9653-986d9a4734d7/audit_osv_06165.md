# [M] Integer overflow in multiple Redis commands can lead to denial-of-service

## Summary
Severity: Medium
Advisory: BIT-keydb-2023-22458
Aliases: BIT-redis-2023-22458, BIT-valkey-2023-22458, CVE-2023-22458, GHSA-r8w2-2m53-gprj
Ecosystem: Bitnami
Published: 2024-08-22
Source: https://osv.dev/vulnerability/BIT-keydb-2023-22458
Type: osv

## Affected
- Bitnami: `keydb` — affected >=7.0.0 <7.0.8

## Details
Redis is an in-memory database that persists on disk. Authenticated users can issue a `HRANDFIELD` or `ZRANDMEMBER` command with specially crafted arguments to trigger a denial-of-service by crashing Redis with an assertion failure. This problem affects Redis versions 6.2 or newer up to but not including 6.2.9 as well as versions 7.0 up to but not including 7.0.8. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/redis/redis/commit/16f408b1a0121cacd44cbf8aee275d69dc627f02
- https://github.com/redis/redis/releases/tag/6.2.9
- https://github.com/redis/redis/releases/tag/7.0.8
- https://github.com/redis/redis/security/advisories/GHSA-r8w2-2m53-gprj
- https://nvd.nist.gov/vuln/detail/CVE-2023-22458
