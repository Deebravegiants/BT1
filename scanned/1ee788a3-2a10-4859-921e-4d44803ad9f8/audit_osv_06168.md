# [H] Heap overflow in COMMAND GETKEYS and ACL evaluation in Redis

## Summary
Severity: High
Advisory: BIT-keydb-2023-36824
Aliases: BIT-redis-2023-36824, BIT-valkey-2023-36824, CVE-2023-36824, GHSA-4cfx-h9gq-xpx3
Ecosystem: Bitnami
Published: 2024-08-22
Source: https://osv.dev/vulnerability/BIT-keydb-2023-36824
Type: osv

## Affected
- Bitnami: `keydb` — affected >=7.0.0 <7.0.12

## Details
Redis is an in-memory database that persists on disk. In Redit 7.0 prior to 7.0.12, extracting key names from a command and a list of arguments may, in some cases, trigger a heap overflow and result in reading random heap memory, heap corruption and potentially remote code execution. Several scenarios that may lead to authenticated users executing a specially crafted `COMMAND GETKEYS` or `COMMAND GETKEYSANDFLAGS`and authenticated users who were set with ACL rules that match key names, executing a specially crafted command that refers to a variadic list of key names. The vulnerability is patched in Redis 7.0.12.

## References
- https://github.com/redis/redis/releases/tag/7.0.12
- https://github.com/redis/redis/security/advisories/GHSA-4cfx-h9gq-xpx3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MIF5MAGYARYUMRFK7PQI7HYXMK2HZE5T/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TDNNH2ONMVNBQ6LUIAOAGDNFPKXNST5K/
- https://security.netapp.com/advisory/ntap-20230814-0009/
- https://nvd.nist.gov/vuln/detail/CVE-2023-36824
