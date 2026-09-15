# [C] ALPINE-CVE-2025-27151

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2025-27151
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-27151
Type: osv

## Affected
- Alpine:v3.18: `redis` — affected >=7.0.0 <7.0.15-r4
- Alpine:v3.19: `redis` — affected >=7.0.0 <7.2.9-r0
- Alpine:v3.20: `valkey` — affected >=0 <7.2.9-r1
- Alpine:v3.21: `valkey` — affected >=0 <7.2.9-r1
- Alpine:v3.22: `valkey` — affected >=0 <8.1.1-r1
- Alpine:v3.23: `valkey` — affected >=0 <8.1.1-r1
- Alpine:v3.24: `valkey` — affected >=0 <8.1.1-r1

## Details
Redis is an open source, in-memory database that persists on disk. In versions starting from 7.0.0 to before 8.0.2, a stack-based buffer overflow exists in redis-check-aof due to the use of memcpy with strlen(filepath) when copying a user-supplied file path into a fixed-size stack buffer. This allows an attacker to overflow the stack and potentially achieve code execution. This issue has been patched in version 8.0.2.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-27151
