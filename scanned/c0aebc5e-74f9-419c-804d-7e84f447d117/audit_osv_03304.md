# [H] ALPINE-CVE-2025-48367

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-48367
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-48367
Type: osv

## Affected
- Alpine:v3.20: `valkey` — affected >=0 <7.2.11-r0
- Alpine:v3.21: `valkey` — affected >=0 <7.2.11-r0
- Alpine:v3.22: `valkey` — affected >=0 <8.1.1-r2
- Alpine:v3.23: `valkey` — affected >=0 <8.1.1-r2
- Alpine:v3.24: `valkey` — affected >=0 <8.1.1-r2

## Details
Redis is an open source, in-memory database that persists on disk. An unauthenticated connection can cause repeated IP protocol errors, leading to client starvation and, ultimately, a denial of service. This vulnerability is fixed in 8.0.3, 7.4.5, 7.2.10, and 6.2.19.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-48367
