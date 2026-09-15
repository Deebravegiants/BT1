# [H] Redis allows out of bounds writes in hyperloglog commands leading to RCE

## Summary
Severity: High
Advisory: BIT-keydb-2025-32023
Aliases: BIT-redis-2025-32023, BIT-valkey-2025-32023, CVE-2025-32023, GHSA-rp2m-q4j6-gr43
Ecosystem: Bitnami
Published: 2025-10-16
Source: https://osv.dev/vulnerability/BIT-keydb-2025-32023
Type: osv

## Affected
- Bitnami: `keydb` — affected >=7.4.0 <7.4.5

## Details
Redis is an open source, in-memory database that persists on disk. From 2.8 to before 8.0.3, 7.4.5, 7.2.10, and 6.2.19, an authenticated user may use a specially crafted string to trigger a stack/heap out of bounds write on hyperloglog operations, potentially leading to remote code execution. The bug likely affects all Redis versions with hyperloglog operations implemented. This vulnerability is fixed in 8.0.3, 7.4.5, 7.2.10, and 6.2.19. An additional workaround to mitigate the problem without patching the redis-server executable is to prevent users from executing hyperloglog operations. This can be done using ACL to restrict HLL commands.

## References
- https://github.com/redis/redis/commit/50188747cbfe43528d2719399a2a3c9599169445
- https://github.com/redis/redis/releases/tag/6.2.19
- https://github.com/redis/redis/releases/tag/7.2.10
- https://github.com/redis/redis/releases/tag/7.4.5
- https://github.com/redis/redis/releases/tag/8.0.3
- https://github.com/redis/redis/security/advisories/GHSA-rp2m-q4j6-gr43
- https://nvd.nist.gov/vuln/detail/CVE-2025-32023
- https://www.exploit-db.com/exploits/52477
