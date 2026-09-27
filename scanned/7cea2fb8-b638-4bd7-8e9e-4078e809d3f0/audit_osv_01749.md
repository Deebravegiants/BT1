# [H] ALPINE-CVE-2020-14147

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-14147
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-06-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14147
Type: osv

## Affected
- Alpine:v3.13: `redis` — affected >=6.0.0 <6.0.3-r0
- Alpine:v3.14: `redis` — affected >=6.0.0 <6.0.3-r0
- Alpine:v3.15: `redis` — affected >=6.0.0 <6.0.3-r0
- Alpine:v3.16: `redis` — affected >=6.0.0 <6.0.3-r0
- Alpine:v3.17: `redis` — affected >=6.0.0 <6.0.3-r0
- Alpine:v3.18: `redis` — affected >=6.0.0 <6.0.3-r0
- Alpine:v3.19: `redis` — affected >=6.0.0 <6.0.3-r0

## Details
An integer overflow in the getnum function in lua_struct.c in Redis before 6.0.3 allows context-dependent attackers with permission to run Lua code in a Redis session to cause a denial of service (memory corruption and application crash) or possibly bypass intended sandbox restrictions via a large number, which triggers a stack-based buffer overflow. NOTE: this issue exists because of a CVE-2015-8080 regression.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14147
