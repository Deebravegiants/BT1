# [H] ALPINE-CVE-2021-32627

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-32627
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-32627
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
Redis is an open source, in-memory database that persists on disk. In affected versions an integer overflow bug in Redis can be exploited to corrupt the heap and potentially result with remote code execution. The vulnerability involves changing the default proto-max-bulk-len and client-query-buffer-limit configuration parameters to very large values and constructing specially crafted very large stream elements. The problem is fixed in Redis 6.2.6, 6.0.16 and 5.0.14. For users unable to upgrade an additional workaround to mitigate the problem without patching the redis-server executable is to prevent users from modifying the proto-max-bulk-len configuration parameter. This can be done using ACL to restrict unprivileged users from using the CONFIG SET command.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-32627
