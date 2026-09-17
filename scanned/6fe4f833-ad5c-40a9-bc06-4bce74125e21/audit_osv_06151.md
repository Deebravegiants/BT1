# [H] Integer overflow issue with Streams in Redis

## Summary
Severity: High
Advisory: BIT-keydb-2021-32627
Aliases: BIT-redis-2021-32627, BIT-valkey-2021-32627, CVE-2021-32627, GHSA-f434-69fm-g45v
Ecosystem: Bitnami
Published: 2024-08-22
Source: https://osv.dev/vulnerability/BIT-keydb-2021-32627
Type: osv

## Affected
- Bitnami: `keydb` — affected >=6.2.0 <6.2.6

## Details
Redis is an open source, in-memory database that persists on disk. In affected versions an integer overflow bug in Redis can be exploited to corrupt the heap and potentially result with remote code execution. The vulnerability involves changing the default proto-max-bulk-len and client-query-buffer-limit configuration parameters to very large values and constructing specially crafted very large stream elements. The problem is fixed in Redis 6.2.6, 6.0.16 and 5.0.14. For users unable to upgrade an additional workaround to mitigate the problem without patching the redis-server executable is to prevent users from modifying the proto-max-bulk-len configuration parameter. This can be done using ACL to restrict unprivileged users from using the CONFIG SET command.

## References
- https://github.com/redis/redis/commit/f6a40570fa63d5afdd596c78083d754081d80ae3
- https://github.com/redis/redis/security/advisories/GHSA-f434-69fm-g45v
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HTYQ5ZF37HNGTZWVNJD3VXP7I6MEEF42/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VL5KXFN3ATM7IIM7Q4O4PWTSRGZ5744Z/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WR5WKJWXD4D6S3DJCZ56V74ESLTDQRAB/
- https://security.gentoo.org/glsa/202209-17
- https://security.netapp.com/advisory/ntap-20211104-0003/
- https://www.debian.org/security/2021/dsa-5001
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-32627
