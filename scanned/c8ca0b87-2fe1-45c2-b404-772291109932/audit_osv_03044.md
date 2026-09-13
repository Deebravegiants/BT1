# [H] ALPINE-CVE-2024-31449

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-31449
Ecosystem: Alpine:v3.15, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-31449
Type: osv

## Affected
- Alpine:v3.15: `redis` — affected >=2.8.18 <6.2.18-r0
- Alpine:v3.17: `redis` — affected >=2.8.18 <7.0.15-r1
- Alpine:v3.18: `redis` — affected >=2.8.18 <7.0.15-r1
- Alpine:v3.19: `redis` — affected >=2.8.18 <7.2.4-r1
- Alpine:v3.20: `valkey` — affected >=0 <7.2.7-r0
- Alpine:v3.21: `valkey` — affected >=0 <7.2.7-r0
- Alpine:v3.22: `valkey` — affected >=0 <7.2.7-r0
- Alpine:v3.23: `valkey` — affected >=0 <7.2.7-r0
- Alpine:v3.24: `valkey` — affected >=0 <7.2.7-r0

## Details
Redis is an open source, in-memory database that persists on disk. An authenticated user may use a specially crafted Lua script to trigger a stack buffer overflow in the bit library, which may potentially lead to remote code execution. The problem exists in all versions of Redis with Lua scripting. This problem has been fixed in Redis versions 6.2.16, 7.2.6, and 7.4.1. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-31449
