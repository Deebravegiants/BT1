# [M] ALPINE-CVE-2022-35977

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-35977
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-35977
Type: osv

## Affected
- Alpine:v3.14: `redis` — affected >=6.0.0 <6.2.9-r0
- Alpine:v3.15: `redis` — affected >=6.0.0 <6.2.9-r0
- Alpine:v3.16: `redis` — affected >=6.0.0 <7.0.8-r0
- Alpine:v3.17: `redis` — affected >=6.0.0 <7.0.8-r0
- Alpine:v3.18: `redis` — affected >=6.0.0 <7.0.8-r0
- Alpine:v3.19: `redis` — affected >=6.0.0 <7.0.8-r0

## Details
Redis is an in-memory database that persists on disk. Authenticated users issuing specially crafted `SETRANGE` and `SORT(_RO)` commands can trigger an integer overflow, resulting with Redis attempting to allocate impossible amounts of memory and abort with an out-of-memory (OOM) panic. The problem is fixed in Redis versions 7.0.8, 6.2.9 and 6.0.17. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-35977
