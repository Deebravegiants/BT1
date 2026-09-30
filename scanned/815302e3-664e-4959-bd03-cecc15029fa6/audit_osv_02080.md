# [H] ALPINE-CVE-2021-21309

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-21309
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-21309
Type: osv

## Affected
- Alpine:v3.10: `redis` — affected >=4.0 <5.0.11-r0
- Alpine:v3.11: `redis` — affected >=4.0 <5.0.11-r0
- Alpine:v3.12: `redis` — affected >=4.0 <5.0.11-r0
- Alpine:v3.13: `redis` — affected >=4.0 <6.0.11-r0
- Alpine:v3.14: `redis` — affected >=4.0 <6.2.0-r0
- Alpine:v3.15: `redis` — affected >=4.0 <6.2.0-r0
- Alpine:v3.16: `redis` — affected >=4.0 <6.2.0-r0
- Alpine:v3.17: `redis` — affected >=4.0 <6.2.0-r0
- Alpine:v3.18: `redis` — affected >=4.0 <6.2.0-r0
- Alpine:v3.19: `redis` — affected >=4.0 <6.2.0-r0

## Details
Redis is an open-source, in-memory database that persists on disk. In affected versions of Redis an integer overflow bug in 32-bit Redis version 4.0 or newer could be exploited to corrupt the heap and potentially result with remote code execution. Redis 4.0 or newer uses a configurable limit for the maximum supported bulk input size. By default, it is 512MB which is a safe value for all platforms. If the limit is significantly increased, receiving a large request from a client may trigger several integer overflow scenarios, which would result with buffer overflow and heap corruption. We believe this could in certain conditions be exploited for remote code execution. By default, authenticated Redis users have access to all configuration parameters and can therefore use the “CONFIG SET proto-max-bulk-len” to change the safe default, making the system vulnerable. **This problem only affects 32-bit Redis (on a 32-bit system, or as a 32-bit executable running on a 64-bit system).** The problem is fixed in version 6.2, and the fix is back ported to 6.0.11 and 5.0.11. Make sure you use one of these versions if you are running 32-bit Redis. An additional workaround to mitigate the problem without patching the redis-server executable is to prevent clients from directly executing `CONFIG SET`: Using Redis 6.0 or newer, ACL configuration can be used to block the command. Using older versions, the `rename-command` configuration directive can be used to rename the command to a random string unknown to users, rendering it inaccessible. Please note that this workaround may have an additional impact on users or operational systems that expect `CONFIG SET` to behave in certain ways.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-21309
