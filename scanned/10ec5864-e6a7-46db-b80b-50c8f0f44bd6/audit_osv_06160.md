# [H] Heap overflow issue with the Lua cjson library used by Redis

## Summary
Severity: High
Advisory: BIT-keydb-2022-24834
Aliases: BIT-redis-2022-24834, BIT-valkey-2022-24834, CVE-2022-24834, GHSA-p8x2-9v9q-c838
Ecosystem: Bitnami
Published: 2024-08-22
Source: https://osv.dev/vulnerability/BIT-keydb-2022-24834
Type: osv

## Affected
- Bitnami: `keydb` — affected >=7.0.0 <7.0.12

## Details
Redis is an in-memory database that persists on disk. A specially crafted Lua script executing in Redis can trigger a heap overflow in the cjson library, and result with heap corruption and potentially remote code execution. The problem exists in all versions of Redis with Lua scripting support, starting from 2.6, and affects only authenticated and authorized users. The problem is fixed in versions 7.0.12, 6.2.13, and 6.0.20.

## References
- https://github.com/redis/redis/security/advisories/GHSA-p8x2-9v9q-c838
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MIF5MAGYARYUMRFK7PQI7HYXMK2HZE5T/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TDNNH2ONMVNBQ6LUIAOAGDNFPKXNST5K/
- https://security.netapp.com/advisory/ntap-20230814-0006/
- https://nvd.nist.gov/vuln/detail/CVE-2022-24834
