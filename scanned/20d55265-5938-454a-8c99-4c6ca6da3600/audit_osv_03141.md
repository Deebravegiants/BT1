# [M] ALPINE-CVE-2024-51741

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-51741
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-51741
Type: osv

## Affected
- Alpine:v3.18: `redis` — affected >=7.0.0 <7.0.15-r2
- Alpine:v3.19: `redis` — affected >=7.0.0 <7.2.7-r0
- Alpine:v3.20: `valkey` — affected >=0 <7.2.8-r0
- Alpine:v3.21: `valkey` — affected >=0 <7.2.8-r0
- Alpine:v3.22: `valkey` — affected >=0 <7.2.8-r0
- Alpine:v3.23: `valkey` — affected >=0 <7.2.8-r0
- Alpine:v3.24: `valkey` — affected >=0 <7.2.8-r0

## Details
Redis is an open source, in-memory database that persists on disk. An authenticated with sufficient privileges may create a malformed ACL selector which, when accessed, triggers a server panic and subsequent denial of service. The problem is fixed in Redis 7.2.7 and 7.4.2.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-51741
