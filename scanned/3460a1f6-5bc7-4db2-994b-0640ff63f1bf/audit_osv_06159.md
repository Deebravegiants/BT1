# [M] A Malformed Lua script can crash Redis

## Summary
Severity: Medium
Advisory: BIT-keydb-2022-24736
Aliases: BIT-redis-2022-24736, BIT-valkey-2022-24736, CVE-2022-24736, GHSA-3qpw-7686-5984
Ecosystem: Bitnami
Published: 2024-08-22
Source: https://osv.dev/vulnerability/BIT-keydb-2022-24736
Type: osv

## Affected
- Bitnami: `keydb` — affected >=0 <6.2.7

## Details
Redis is an in-memory database that persists on disk. Prior to versions 6.2.7 and 7.0.0, an attacker attempting to load a specially crafted Lua script can cause NULL pointer dereference which will result with a crash of the redis-server process. The problem is fixed in Redis versions 7.0.0 and 6.2.7. An additional workaround to mitigate this problem without patching the redis-server executable, if Lua scripting is not being used, is to block access to `SCRIPT LOAD` and `EVAL` commands using ACL rules.

## References
- https://github.com/redis/redis/pull/10651
- https://github.com/redis/redis/releases/tag/6.2.7
- https://github.com/redis/redis/releases/tag/7.0.0
- https://github.com/redis/redis/security/advisories/GHSA-3qpw-7686-5984
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/J4ZK3675DGHVVDOFLJN7WX6YYH27GPMK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VPYKSG7LKUJGVM2P72EHXKVRVRWHLORX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WSTPUCAPBRHIFPSCOURR4OYX4E2OISAF/
- https://security.gentoo.org/glsa/202209-17
- https://security.netapp.com/advisory/ntap-20220715-0003/
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2022-24736
