# [M] Integer Overflow in several Redis commands can lead to denial of service.

## Summary
Severity: Medium
Advisory: BIT-redis-2023-25155
Aliases: BIT-keydb-2023-25155, BIT-valkey-2023-25155, CVE-2023-25155, GHSA-x2r7-j9vw-3w83
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-redis-2023-25155
Type: osv

## Affected
- Bitnami: `redis` — affected >=7.0.0 <7.0.9

## Details
Redis is an in-memory database that persists on disk. Authenticated users issuing specially crafted `SRANDMEMBER`, `ZRANDMEMBER`, and `HRANDFIELD` commands can trigger an integer overflow, resulting in a runtime assertion and termination of the Redis server process. This problem affects all Redis versions. Patches were released in Redis version(s) 6.0.18, 6.2.11 and 7.0.9.

## References
- https://github.com/redis/redis/commit/2a2a582e7cd99ba3b531336b8bd41df2b566e619
- https://github.com/redis/redis/releases/tag/6.0.18
- https://github.com/redis/redis/releases/tag/6.2.11
- https://github.com/redis/redis/releases/tag/7.0.9
- https://github.com/redis/redis/security/advisories/GHSA-x2r7-j9vw-3w83
- https://nvd.nist.gov/vuln/detail/CVE-2023-25155
