# [M] Denial-of-service due to unbounded pattern matching in Redis

## Summary
Severity: Medium
Advisory: BIT-keydb-2024-31228
Aliases: BIT-redis-2024-31228, BIT-valkey-2024-31228, CVE-2024-31228, GHSA-66gq-c942-6976
Ecosystem: Bitnami
Published: 2024-10-09
Source: https://osv.dev/vulnerability/BIT-keydb-2024-31228
Type: osv

## Affected
- Bitnami: `keydb` — affected >=7.0.0 <6.3.4

## Details
Redis is an open source, in-memory database that persists on disk. Authenticated users can trigger a denial-of-service by using specially crafted, long string match patterns on supported commands such as `KEYS`, `SCAN`, `PSUBSCRIBE`, `FUNCTION LIST`, `COMMAND LIST` and ACL definitions. Matching of extremely long patterns may result in unbounded recursion, leading to stack overflow and process crash. This problem has been fixed in Redis versions 6.2.16, 7.2.6, and 7.4.1. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/redis/redis/commit/9317bf64659b33166a943ec03d5d9b954e86afb0
- https://github.com/redis/redis/security/advisories/GHSA-66gq-c942-6976
- https://nvd.nist.gov/vuln/detail/CVE-2024-31228
- https://lists.debian.org/debian-lts-announce/2024/11/msg00031.html
