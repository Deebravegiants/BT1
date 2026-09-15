# [H] Lua library commands may lead to stack overflow and RCE in Redis

## Summary
Severity: High
Advisory: BIT-keydb-2024-31449
Aliases: BIT-redis-2024-31449, BIT-valkey-2024-31449, CVE-2024-31449, GHSA-whxg-wx83-85p5
Ecosystem: Bitnami
Published: 2024-10-09
Source: https://osv.dev/vulnerability/BIT-keydb-2024-31449
Type: osv

## Affected
- Bitnami: `keydb` — affected >=7.0.0 <6.3.4

## Details
Redis is an open source, in-memory database that persists on disk. An authenticated user may use a specially crafted Lua script to trigger a stack buffer overflow in the bit library, which may potentially lead to remote code execution. The problem exists in all versions of Redis with Lua scripting. This problem has been fixed in Redis versions 6.2.16, 7.2.6, and 7.4.1. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/redis/redis/commit/1f7c148be2cbacf7d50aa461c58b871e87cc5ed9
- https://github.com/redis/redis/security/advisories/GHSA-whxg-wx83-85p5
- https://nvd.nist.gov/vuln/detail/CVE-2024-31449
