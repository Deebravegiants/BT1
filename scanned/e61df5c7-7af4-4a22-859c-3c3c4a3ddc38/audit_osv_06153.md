# [M] Vulnerability in Lua Debugger in Redis

## Summary
Severity: Medium
Advisory: BIT-keydb-2021-32672
Aliases: BIT-redis-2021-32672, BIT-valkey-2021-32672, CVE-2021-32672, GHSA-9mj9-xx53-qmxm
Ecosystem: Bitnami
Published: 2024-08-22
Source: https://osv.dev/vulnerability/BIT-keydb-2021-32672
Type: osv

## Affected
- Bitnami: `keydb` — affected >=6.2.0 <6.2.6

## Details
Redis is an open source, in-memory database that persists on disk. When using the Redis Lua Debugger, users can send malformed requests that cause the debugger’s protocol parser to read data beyond the actual buffer. This issue affects all versions of Redis with Lua debugging support (3.2 or newer). The problem is fixed in versions 6.2.6, 6.0.16 and 5.0.14.

## References
- https://github.com/redis/redis/commit/6ac3c0b7abd35f37201ed2d6298ecef4ea1ae1dd
- https://github.com/redis/redis/security/advisories/GHSA-9mj9-xx53-qmxm
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HTYQ5ZF37HNGTZWVNJD3VXP7I6MEEF42/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VL5KXFN3ATM7IIM7Q4O4PWTSRGZ5744Z/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WR5WKJWXD4D6S3DJCZ56V74ESLTDQRAB/
- https://security.gentoo.org/glsa/202209-17
- https://security.netapp.com/advisory/ntap-20211104-0003/
- https://www.debian.org/security/2021/dsa-5001
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-32672
