# [H] ALPINE-CVE-2025-21605

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-21605
Ecosystem: Alpine:v3.15, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-21605
Type: osv

## Affected
- Alpine:v3.15: `redis` — affected >=2.6.0 <6.2.18-r0
- Alpine:v3.18: `redis` — affected >=2.6.0 <7.0.15-r3
- Alpine:v3.19: `redis` — affected >=2.6.0 <7.2.8-r0
- Alpine:v3.20: `valkey` — affected >=7.2.4 <7.2.9-r0
- Alpine:v3.21: `valkey` — affected >=7.2.4 <7.2.9-r0
- Alpine:v3.22: `valkey` — affected >=7.2.4 <7.2.9-r0
- Alpine:v3.23: `valkey` — affected >=7.2.4 <7.2.9-r0
- Alpine:v3.24: `valkey` — affected >=7.2.4 <7.2.9-r0

## Details
Redis is an open source, in-memory database that persists on disk. In versions starting at 2.6 and prior to 7.4.3, An unauthenticated client can cause unlimited growth of output buffers, until the server runs out of memory or is killed. By default, the Redis configuration does not limit the output buffer of normal clients (see client-output-buffer-limit). Therefore, the output buffer can grow unlimitedly over time. As a result, the service is exhausted and the memory is unavailable. When password authentication is enabled on the Redis server, but no password is provided, the client can still cause the output buffer to grow from "NOAUTH" responses until the system will run out of memory. This issue has been patched in version 7.4.3. An additional workaround to mitigate this problem without patching the redis-server executable is to block access to prevent unauthenticated users from connecting to Redis. This can be done in different ways. Either using network access control tools like firewalls, iptables, security groups, etc, or enabling TLS and requiring users to authenticate using client side certificates.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-21605
