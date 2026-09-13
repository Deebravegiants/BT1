# [M] ALPINE-CVE-2024-31228

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-31228
Ecosystem: Alpine:v3.15, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-31228
Type: osv

## Affected
- Alpine:v3.15: `redis` — affected >=2.2.5 <6.2.18-r0
- Alpine:v3.17: `redis` — affected >=2.2.5 <7.0.15-r1
- Alpine:v3.18: `redis` — affected >=2.2.5 <7.0.15-r1
- Alpine:v3.19: `redis` — affected >=2.2.5 <7.2.4-r1
- Alpine:v3.20: `valkey` — affected >=0 <7.2.7-r0
- Alpine:v3.21: `valkey` — affected >=0 <7.2.7-r0
- Alpine:v3.22: `valkey` — affected >=0 <7.2.7-r0
- Alpine:v3.23: `valkey` — affected >=0 <7.2.7-r0
- Alpine:v3.24: `valkey` — affected >=0 <7.2.7-r0

## Details
Redis is an open source, in-memory database that persists on disk. Authenticated users can trigger a denial-of-service by using specially crafted, long string match patterns on supported commands such as `KEYS`, `SCAN`, `PSUBSCRIBE`, `FUNCTION LIST`, `COMMAND LIST` and ACL definitions. Matching of extremely long patterns may result in unbounded recursion, leading to stack overflow and process crash. This problem has been fixed in Redis versions 6.2.16, 7.2.6, and 7.4.1. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-31228
