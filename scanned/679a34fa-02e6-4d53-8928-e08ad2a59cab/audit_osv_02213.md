# [H] ALPINE-CVE-2021-32675

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-32675
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-32675
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
Redis is an open source, in-memory database that persists on disk. When parsing an incoming Redis Standard Protocol (RESP) request, Redis allocates memory according to user-specified values which determine the number of elements (in the multi-bulk header) and size of each element (in the bulk header). An attacker delivering specially crafted requests over multiple connections can cause the server to allocate significant amount of memory. Because the same parsing mechanism is used to handle authentication requests, this vulnerability can also be exploited by unauthenticated users. The problem is fixed in Redis versions 6.2.6, 6.0.16 and 5.0.14. An additional workaround to mitigate this problem without patching the redis-server executable is to block access to prevent unauthenticated users from connecting to Redis. This can be done in different ways: Using network access control tools like firewalls, iptables, security groups, etc. or Enabling TLS and requiring users to authenticate using client side certificates.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-32675
