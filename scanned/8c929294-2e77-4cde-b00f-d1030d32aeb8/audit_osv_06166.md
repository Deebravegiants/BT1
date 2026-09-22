# [M] Specially crafted MSETNX command can lead to denial-of-service

## Summary
Severity: Medium
Advisory: BIT-keydb-2023-28425
Aliases: BIT-redis-2023-28425, BIT-valkey-2023-28425, CVE-2023-28425, GHSA-mvmm-4vq6-vw8c
Ecosystem: Bitnami
Published: 2024-08-22
Source: https://osv.dev/vulnerability/BIT-keydb-2023-28425
Type: osv

## Affected
- Bitnami: `keydb` — affected >=7.0.8 <7.0.10

## Details
Redis is an in-memory database that persists on disk. Starting in version 7.0.8 and prior to version 7.0.10, authenticated users can use the MSETNX command to trigger a runtime assertion and termination of the Redis server process. The problem is fixed in Redis version 7.0.10.

## References
- https://github.com/redis/redis/commit/48e0d4788434833b47892fe9f3d91be7687f25c9
- https://github.com/redis/redis/releases/tag/7.0.10
- https://github.com/redis/redis/security/advisories/GHSA-mvmm-4vq6-vw8c
- https://security.netapp.com/advisory/ntap-20230413-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2023-28425
