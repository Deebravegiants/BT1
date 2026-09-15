# [H] ALPINE-CVE-2021-32628

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-32628
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-32628
Type: osv

## Affected
- Alpine:v3.11: `redis` — affected >=5.0.0 <5.0.14-r0
- Alpine:v3.12: `redis` — affected >=5.0.0 <5.0.14-r0
- Alpine:v3.13: `redis` — affected >=5.0.0 <6.0.16-r0
- Alpine:v3.14: `redis` — affected >=5.0.0 <6.2.6-r0
- Alpine:v3.15: `redis` — affected >=5.0.0 <6.2.6-r0
- Alpine:v3.16: `redis` — affected >=5.0.0 <6.2.6-r0
- Alpine:v3.17: `redis` — affected >=5.0.0 <6.2.6-r0
- Alpine:v3.18: `redis` — affected >=5.0.0 <6.2.6-r0
- Alpine:v3.19: `redis` — affected >=5.0.0 <6.2.6-r0

## Details
Redis is an open source, in-memory database that persists on disk. An integer overflow bug in the ziplist data structure used by all versions of Redis can be exploited to corrupt the heap and potentially result with remote code execution. The vulnerability involves modifying the default ziplist configuration parameters (hash-max-ziplist-entries, hash-max-ziplist-value, zset-max-ziplist-entries or zset-max-ziplist-value) to a very large value, and then constructing specially crafted commands to create very large ziplists. The problem is fixed in Redis versions 6.2.6, 6.0.16, 5.0.14. An additional workaround to mitigate the problem without patching the redis-server executable is to prevent users from modifying the above configuration parameters. This can be done using ACL to restrict unprivileged users from using the CONFIG SET command.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-32628
