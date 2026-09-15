# [H] CVE-2021-29478

## Summary
Severity: High
Advisory: CVE-2021-29478
Aliases: GHSA-qh52-crrg-44g3
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-04
Source: https://osv.dev/vulnerability/CVE-2021-29478
Type: osv

## Details
Redis is an open source (BSD licensed), in-memory data structure store, used as a database, cache, and message broker. An integer overflow bug in Redis 6.2 before 6.2.3 could be exploited to corrupt the heap and potentially result with remote code execution. Redis 6.0 and earlier are not directly affected by this issue. The problem is fixed in version 6.2.3. An additional workaround to mitigate the problem without patching the `redis-server` executable is to prevent users from modifying the `set-max-intset-entries` configuration parameter. This can be done using ACL to restrict unprivileged users from using the `CONFIG SET` command.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BPWBIZXA67JFIB63W2CNVVILCGIC2ME5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EZJ6JGQ2ETZB2DWTQSGCOGG7EF3ILV4V/
- https://redis.io/
- https://github.com/redis/redis/security/advisories/GHSA-qh52-crrg-44g3
- https://security.gentoo.org/glsa/202107-20
