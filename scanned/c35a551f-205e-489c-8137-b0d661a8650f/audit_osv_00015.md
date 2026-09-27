# [H] ALPINE-CVE-2015-8080

## Summary
Severity: High
Advisory: ALPINE-CVE-2015-8080
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2015-8080
Type: osv

## Affected
- Alpine:v3.10: `redis` — affected >=2.8.0 <5.0.5-r1
- Alpine:v3.11: `redis` — affected >=2.8.0 <5.0.7-r1
- Alpine:v3.12: `redis` — affected >=2.8.0 <5.0.8-r0
- Alpine:v3.13: `redis` — affected >=2.8.0 <5.0.8-r0
- Alpine:v3.14: `redis` — affected >=2.8.0 <5.0.8-r0
- Alpine:v3.15: `redis` — affected >=2.8.0 <5.0.8-r0
- Alpine:v3.16: `redis` — affected >=2.8.0 <5.0.8-r0
- Alpine:v3.17: `redis` — affected >=2.8.0 <5.0.8-r0
- Alpine:v3.18: `redis` — affected >=2.8.0 <5.0.8-r0
- Alpine:v3.19: `redis` — affected >=2.8.0 <5.0.8-r0

## Details
Integer overflow in the getnum function in lua_struct.c in Redis 2.8.x before 2.8.24 and 3.0.x before 3.0.6 allows context-dependent attackers with permission to run Lua code in a Redis session to cause a denial of service (memory corruption and application crash) or possibly bypass intended sandbox restrictions via a large number, which triggers a stack-based buffer overflow.

## References
- https://security.alpinelinux.org/vuln/CVE-2015-8080
