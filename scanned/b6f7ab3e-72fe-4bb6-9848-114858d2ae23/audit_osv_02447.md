# [M] ALPINE-CVE-2022-24736

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-24736
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-04-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-24736
Type: osv

## Affected
- Alpine:v3.14: `redis` — affected >=0 <6.2.7-r0
- Alpine:v3.15: `redis` — affected >=0 <6.2.7-r0
- Alpine:v3.16: `redis` — affected >=0 <6.2.7-r0
- Alpine:v3.17: `redis` — affected >=0 <6.2.7-r0
- Alpine:v3.18: `redis` — affected >=0 <6.2.7-r0
- Alpine:v3.19: `redis` — affected >=0 <6.2.7-r0

## Details
Redis is an in-memory database that persists on disk. Prior to versions 6.2.7 and 7.0.0, an attacker attempting to load a specially crafted Lua script can cause NULL pointer dereference which will result with a crash of the redis-server process. The problem is fixed in Redis versions 7.0.0 and 6.2.7. An additional workaround to mitigate this problem without patching the redis-server executable, if Lua scripting is not being used, is to block access to `SCRIPT LOAD` and `EVAL` commands using ACL rules.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-24736
